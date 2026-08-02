import shutil
import typer
from pathlib import Path
import structlog
from rune.repositories import git_repository
from rune.services import (
    rule_service,
    module_service,
    skill_service,
    map_service,
    mcp_service,
    workspace_service,
)

app = typer.Typer(
    no_args_is_help=True, help="Manage agents context, rules, skills, and map."
)
logger = structlog.get_logger(__name__)


@app.command("update")
def update(global_scope: bool = typer.Option(False, "--global", "-g")):
    """Update and repair all agent contexts (rules, skills, modules, MCP) across target agents."""
    cwd = Path.cwd()
    git_root = git_repository.get_git_root(cwd) or cwd

    # Step 1: Rules
    try:
        module_service.update_modules(git_root, type="rules", global_scope=global_scope)
        rule_dirs = rule_service.discover_rule_dirs(git_root)
        if rule_dirs:
            for rule_dir in rule_dirs:
                if (rule_dir / ".git").exists():
                    git_repository.update_submodules(rule_dir)
        logger.info("Successfully updated rules.")
    except Exception:
        logger.exception("Failed to update rules.")

    # Step 2: Skills and SKILL.md Instructions & Multi-Agent Repair
    try:
        module_service.update_modules(
            git_root, type="skills", global_scope=global_scope
        )
        module_service.update_modules(
            git_root, type="modules", global_scope=global_scope
        )
        skills = skill_service.discover_skills(git_root)
        if skills:
            target_agents = workspace_service.resolve_target_agents(
                git_root, cwd, global_scope, None
            ) or [".agents"]
            for skill in skills:
                skill_dir = (
                    (git_root / skill.path).resolve() if skill.path else git_root
                )
                skill_service.update_skill_instructions(skill_dir)

                # Sync/repair skill across all target agent folders
                for agent in target_agents:
                    target_skill_dir = (
                        git_root / agent / "skills" / skill.name
                    ).resolve()
                    if skill_dir != target_skill_dir and skill_dir.exists():
                        target_skill_dir.parent.mkdir(parents=True, exist_ok=True)
                        if not target_skill_dir.exists():
                            shutil.copytree(
                                skill_dir, target_skill_dir, dirs_exist_ok=True
                            )
                            logger.info(
                                f"Repaired skill '{skill.name}' in target agent '{agent}'."
                            )

        logger.info(
            "Successfully updated and repaired skills and SKILL.md context instructions."
        )
    except Exception:
        logger.exception("Failed to update skills.")

    # Step 3: Merge Rules into AGENTS.md
    try:
        rule_service.merge_rules_to_agents_md(git_root)
        logger.info("Successfully merged rules into AGENTS.md.")
    except Exception:
        logger.exception("Failed to merge rules into AGENTS.md.")

    # Step 4: Generate Probe Context Guidelines and Merge into AGENTS.md
    try:
        logger.info("Updating AGENTS.md with Probe context instructions...")
        repo_ast = map_service.generate_submodule_map(git_root)
        map_service.merge_ast_to_agents_md(git_root, repo_ast)
        logger.info("Successfully updated AGENTS.md with Probe context guidance.")
    except Exception:
        logger.exception("Failed to update AGENTS.md with Probe context guidance.")

    # Step 5: Update MCP configurations
    try:
        mcp_service.add_mcp_server(
            "probelabs/probe", git_root=git_root, cwd=cwd, global_scope=global_scope
        )
        logger.info("Successfully updated MCP configurations.")
    except Exception:
        logger.exception("Failed to update MCP configurations.")
