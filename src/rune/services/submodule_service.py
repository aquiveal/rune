import shutil
import sys
from pathlib import Path

import questionary
import structlog

from rune.config.main import settings
from rune.repositories import config_repository, index_repository, mcp_repository
from rune.schemas.index_schema import IndexItemSchema
from rune.services import (
    map_service,
    mcp_service,
    module_service,
    rule_service,
    skill_service,
    workspace_service,
)

__all__ = [
    "detect_potential_submodules",
    "get_configured_submodules",
    "merge_submodules_upward_to_workspace",
    "prompt_and_configure_submodules",
    "propagate_workspace_to_submodule",
    "update_all_submodules",
]

logger = structlog.get_logger(__name__)


def detect_potential_submodules(workspace_root: Path) -> list[Path]:
    """Detect candidate submodule directory paths from .gitmodules file."""
    gitmodules = workspace_root / ".gitmodules"
    candidates: list[Path] = []

    if gitmodules.exists():
        try:
            content = gitmodules.read_text(encoding="utf-8")
            for line in content.splitlines():
                line = line.strip()
                if line.startswith("path ="):
                    rel_path = line.split("=", 1)[1].strip().replace("\\", "/")
                    sub_dir = workspace_root / Path(rel_path)
                    if (
                        sub_dir.exists()
                        and sub_dir.is_dir()
                        and sub_dir not in candidates
                    ):
                        candidates.append(sub_dir.relative_to(workspace_root))
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Could not parse .gitmodules: {e}")

    return candidates


def get_configured_submodules(workspace_root: Path) -> list[Path]:
    """Get list of existing submodule paths explicitly configured in .rune/config."""
    configured_paths = settings.get_submodule_paths(workspace_root)
    result = []
    for p in configured_paths:
        try:
            rel_p = p.relative_to(workspace_root)
            if p.exists() and p.is_dir() and rel_p not in result:
                result.append(p)
        except ValueError:
            if p.exists() and p.is_dir() and p not in result:
                result.append(p)
    return result


def prompt_and_configure_submodules(workspace_root: Path) -> list[Path]:
    """Interactively prompt user to select detected submodules to track in .rune/config."""
    candidates = detect_potential_submodules(workspace_root)
    if not candidates:
        return get_configured_submodules(workspace_root)

    already_configured = [
        str(p.relative_to(workspace_root) if p.is_absolute() else p)
        for p in get_configured_submodules(workspace_root)
    ]
    unconfigured_candidates = [
        str(c) for c in candidates if str(c) not in already_configured
    ]

    if unconfigured_candidates and sys.stdin.isatty():
        try:
            selected = questionary.checkbox(
                "Select git submodule(s) to track with Rune:",
                choices=unconfigured_candidates,
            ).ask()
            if selected:
                for sel in selected:
                    config_repository.add_submodule_path(workspace_root, sel)
                # Re-reload settings
                settings.submodules.extend(selected)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Interactive submodule selection skipped: {e}")

    return get_configured_submodules(workspace_root)


def propagate_workspace_to_submodule(workspace_root: Path, submodule_dir: Path):
    """Ensure submodule has basic .rune structure if initialized."""
    if not submodule_dir.exists() or not submodule_dir.is_dir():
        return
    sub_rune = submodule_dir / ".rune"
    sub_rune.mkdir(exist_ok=True)
    (submodule_dir / ".runemodules").touch(exist_ok=True)


def update_all_submodules(workspace_root: Path, global_scope: bool = False):
    """Step 1: Execute rule, skill, module, and map updates inside each configured submodule independently."""
    submodule_dirs = get_configured_submodules(workspace_root)
    if not submodule_dirs:
        return

    for sub_dir in submodule_dirs:
        try:
            rel_str = str(
                sub_dir.relative_to(workspace_root)
                if sub_dir.is_absolute()
                else sub_dir
            )
            logger.info(f"Updating submodule modules and skills inside '{rel_str}'...")

            # Run submodule internal updates
            module_service.update_modules(sub_dir, type="rules", global_scope=False)
            module_service.update_modules(sub_dir, type="skills", global_scope=False)
            module_service.update_modules(sub_dir, type="modules", global_scope=False)

            # Discover submodule skills and update SKILL.md instruction blocks
            sub_skills = skill_service.discover_skills(sub_dir)
            if sub_skills:
                for skill in sub_skills:
                    s_dir = (sub_dir / skill.path).resolve() if skill.path else sub_dir
                    skill_service.update_skill_instructions(s_dir)

            # Re-merge rules inside submodule
            rule_service.merge_rules_to_agents_md(sub_dir)

            # Probe map inside submodule
            repo_ast = map_service.generate_submodule_map(sub_dir)
            map_service.merge_ast_to_agents_md(sub_dir, repo_ast)

            # Probe MCP inside submodule while preserving key
            mcp_service.add_mcp_server(
                "probelabs/probe", git_root=sub_dir, cwd=sub_dir, global_scope=False
            )

            logger.info(f"Successfully updated submodule '{rel_str}'.")
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Failed to update submodule at '{sub_dir}': {e}")


def merge_submodules_upward_to_workspace(workspace_root: Path):
    """Step 3: Merge submodule rules, skills, MCP, and .runemodules UPWARD into workspace context."""
    submodule_dirs = get_configured_submodules(workspace_root)
    if not submodule_dirs:
        return

    target_agents = workspace_service.detect_agents(workspace_root) or [".agents"]

    for sub_dir in submodule_dirs:
        try:
            rel_sub_str = str(
                sub_dir.relative_to(workspace_root)
                if sub_dir.is_absolute()
                else sub_dir
            ).replace("\\", "/")

            # 1. Merge .runemodules UPWARD
            sub_runemodules = sub_dir / ".runemodules"
            parent_runemodules = workspace_root / ".runemodules"
            if sub_runemodules.exists():
                sub_lines = [
                    l.strip()
                    for l in sub_runemodules.read_text(encoding="utf-8").splitlines()
                    if l.strip()
                ]
                parent_content = (
                    parent_runemodules.read_text(encoding="utf-8")
                    if parent_runemodules.exists()
                    else ""
                )
                parent_lines = [
                    l.strip() for l in parent_content.splitlines() if l.strip()
                ]
                missing = [l for l in sub_lines if l not in parent_lines]
                if missing:
                    if parent_content and not parent_content.endswith("\n"):
                        parent_content += "\n"
                    for line in missing:
                        parent_content += f"{line}\n"
                    parent_runemodules.write_text(parent_content, encoding="utf-8")

            # 2. Merge rules and skills UPWARD across target agent folders
            for agent in target_agents:
                sub_agent_dir = sub_dir / agent
                workspace_agent_dir = workspace_root / agent

                if sub_agent_dir.exists() and sub_agent_dir.is_dir():
                    workspace_agent_dir.mkdir(parents=True, exist_ok=True)

                    # Merge skills UPWARD
                    sub_skills_dir = sub_agent_dir / "skills"
                    if sub_skills_dir.exists() and sub_skills_dir.is_dir():
                        ws_skills_dir = workspace_agent_dir / "skills"
                        ws_skills_dir.mkdir(parents=True, exist_ok=True)
                        for item in sub_skills_dir.iterdir():
                            dst_item = ws_skills_dir / item.name
                            if item.is_dir():
                                shutil.copytree(
                                    item,
                                    dst_item,
                                    dirs_exist_ok=True,
                                    ignore_dangling_symlinks=True,
                                )
                                index_repository.record_item(
                                    workspace_root,
                                    IndexItemSchema(
                                        name=item.name,
                                        path=str(
                                            dst_item.relative_to(workspace_root)
                                        ).replace("\\", "/"),
                                        item_type="skill",
                                        origin_scope=f"submodule:{rel_sub_str}",
                                    ),
                                )

                    # Merge rules UPWARD
                    sub_rules_dir = sub_agent_dir / "rules"
                    if sub_rules_dir.exists() and sub_rules_dir.is_dir():
                        ws_rules_dir = workspace_agent_dir / "rules"
                        ws_rules_dir.mkdir(parents=True, exist_ok=True)
                        for item in sub_rules_dir.iterdir():
                            dst_item = ws_rules_dir / item.name
                            if item.is_dir():
                                shutil.copytree(
                                    item,
                                    dst_item,
                                    dirs_exist_ok=True,
                                    ignore_dangling_symlinks=True,
                                )
                            elif item.is_file():
                                shutil.copy2(item, dst_item)
                            index_repository.record_item(
                                workspace_root,
                                IndexItemSchema(
                                    name=item.name,
                                    path=str(
                                        dst_item.relative_to(workspace_root)
                                    ).replace("\\", "/"),
                                    item_type="rule",
                                    origin_scope=f"submodule:{rel_sub_str}",
                                ),
                            )

                    # Merge MCP servers UPWARD
                    sub_mcp_path = mcp_repository.get_agent_mcp_config_path(
                        sub_dir, agent, global_scope=False
                    )
                    ws_mcp_path = mcp_repository.get_agent_mcp_config_path(
                        workspace_root, agent, global_scope=False
                    )

                    if sub_mcp_path.exists():
                        sub_mcp = mcp_repository.load_mcp_config(sub_mcp_path)
                        for s_name, s_cfg in sub_mcp.mcpServers.items():
                            mcp_repository.add_server_config(ws_mcp_path, s_name, s_cfg)

            logger.info(
                f"Merged context from submodule '{rel_sub_str}' UPWARD into workspace."
            )
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Failed to merge submodule '{sub_dir}' upward: {e}")

    # Re-compile parent workspace AGENTS.md with all merged rules
    rule_service.merge_rules_to_agents_md(workspace_root)
