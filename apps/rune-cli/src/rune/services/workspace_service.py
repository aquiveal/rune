from pathlib import Path
from typing import List, Optional

import questionary

from rune.config.main import settings
from rune.repositories import config_repository


def is_initialized(root_dir: Path) -> bool:
    return (root_dir / ".rune").is_dir()


def init_workspace(root_dir: Path):
    rune_dir = root_dir / ".rune"
    (rune_dir / "modules").mkdir(parents=True, exist_ok=True)
    (root_dir / ".runemodules").touch(exist_ok=True)
    (rune_dir / "config").touch(exist_ok=True)
    (rune_dir / "index").touch(exist_ok=True)
    update_gitignore(root_dir)

    # Automatically install probe MCP globally for all agents during init
    try:
        from rune.services import mcp_service

        mcp_service.add_mcp_server(
            "probelabs/probe", git_root=root_dir, cwd=root_dir, global_scope=True
        )
    except Exception:
        pass


def detect_agents(root_dir: Path) -> List[str]:
    detected = []
    if settings.agent.names:
        detected.extend(settings.agent.names)

    for agent in settings.agents:
        if (root_dir / agent).is_dir() and agent not in detected:
            detected.append(agent)

    if (root_dir / ".agents").is_dir() and ".agents" not in detected:
        detected.append(".agents")

    return detected


def resolve_target_agents(
    git_root: Optional[Path],
    cwd: Path,
    global_scope: bool,
    agents_arg: Optional[List[str]],
) -> Optional[List[str]]:
    target_agents = []
    if global_scope:
        if agents_arg:
            target_agents = list(agents_arg)
        else:
            choices = list(settings.agent_paths.keys())
            try:
                selected = questionary.checkbox(
                    "Select target agent(s) for global scope:", choices=choices
                ).ask()
                target_agents = selected if selected else choices
            except Exception:
                target_agents = choices
    elif git_root or cwd:
        root_path = git_root or cwd
        target_agents = list(agents_arg) if agents_arg else detect_agents(root_path)
        if not target_agents and not agents_arg:
            target_agents = [".agents"]
            config_repository.add_agent_name(root_path, ".agents")

        if target_agents is not None and ".agents" not in target_agents:
            target_agents.append(".agents")

    return target_agents


def update_gitignore(root_dir: Path):
    gitignore_file = root_dir / ".gitignore"
    content = gitignore_file.read_text() if gitignore_file.exists() else ""
    lines = content.splitlines()

    # Remove old .rune/ entry if it exists
    if ".rune/" in lines:
        lines.remove(".rune/")
        content = "\n".join(lines)
        if content and not content.endswith("\n"):
            content += "\n"

    entries = [
        ".rune/*",
        "!.rune/config",
        "!.rune/index",
    ]

    missing = [e for e in entries if e not in lines and e.strip("/") not in lines]

    if missing:
        if content and not content.endswith("\n"):
            content += "\n"
        if "# Rune" not in lines:
            content += "\n# Rune\n"
        for e in missing:
            content += f"{e}\n"
        gitignore_file.write_text(content)
