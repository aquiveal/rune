from pathlib import Path
from typing import Annotated

import structlog
import typer

from rune.commands import skills
from rune.config.exceptions import RuneError
from rune.repositories import git_repository
from rune.services import skill_service
from rune.utils.url import parse_github_url, resolve_url

__all__ = []

app = typer.Typer(no_args_is_help=True, help="Manage modules contextually")
logger = structlog.get_logger(__name__)


@app.command("add")
def add(
    url: Annotated[
        str, typer.Argument(help="URL of the git repository to add as a module")
    ],
    target_name: Annotated[
        str | None, typer.Argument(help="Name of the skill/rule to add the module to")
    ] = None,
    force: Annotated[
        bool, typer.Option("--force", "-f", help="Force add the module")
    ] = False,
):
    """Add a module contextually based on the current directory."""
    cwd = Path.cwd()

    git_root = git_repository.get_git_root(cwd) or cwd

    # Resolve the URL (handles aliases and subpaths)
    raw_url = resolve_url(url, git_root)
    base_url, extracted_path = parse_github_url(raw_url)

    # Extract repo name from base_url
    repo_name = base_url.rstrip("/").split("/")[-1]
    repo_name = repo_name.removesuffix(".git")

    target_dir = None
    context = None

    # Determine context
    if cwd.name == "skills":
        context = "skills_root"
        raw_name = target_name or repo_name
        sanitized_name = skill_service.sanitize_skill_name(raw_name)
        if not sanitized_name:
            logger.error(f"Invalid skill name '{raw_name}'.")
            raise typer.Exit(1)
        target_dir = cwd / sanitized_name
    elif cwd.parent.name == "skills":
        context = "inside_skill"
        target_dir = cwd
    else:
        from rune.services import workspace_service

        target_agents = workspace_service.resolve_target_agents(
            git_root=git_root, cwd=cwd, global_scope=False, agents_arg=None
        )
        if not target_agents:
            logger.error(
                "Could not determine target agent directory. Please run inside a 'skills' directory."
            )
            raise typer.Exit(1)

        agent_dir = target_agents[0]
        skills_dir = git_root / agent_dir / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)

        context = "skills_root"
        raw_name = target_name or repo_name
        sanitized_name = skill_service.sanitize_skill_name(raw_name)
        if not sanitized_name:
            logger.error(f"Invalid skill name '{raw_name}'.")
            raise typer.Exit(1)
        target_dir = skills_dir / sanitized_name

    try:
        # Scaffold if necessary
        if context == "skills_root" and not (target_dir / "SKILL.md").exists():
            logger.info(f"Scaffolding new skill '{target_dir.name}'...")
            skills.scaffold_skill(target_dir.name, target_dir.parent)

        # Ensure modules directory exists
        modules_dir = target_dir / "modules"
        modules_dir.mkdir(exist_ok=True)

        module_path = f"modules/{repo_name}"

        from rune.services import module_service

        logger.info(
            f"Adding module {base_url} (path: {extracted_path or '.'}) to {module_path}..."
        )

        try:
            module_service.add_module(
                git_root=git_root,
                cwd=target_dir,
                url=base_url,
                path=extracted_path or ".",
                name=repo_name,
                type="modules",
                agents=[],
                global_scope=False,
                copy_mode=False,
            )
        except Exception as e:
            raise RuneError(f"Failed to fetch module: {e}") from e

        logger.info("Syncing skill instructions...")
        skill_service.update_skill_instructions(target_dir)

        logger.info(f"Successfully added module and updated skill '{target_dir.name}'")

    except typer.Exit:
        raise
    except Exception as e:  # noqa: BLE001
        logger.error(f"Failed to add module: {e}")
        raise typer.Exit(1)
