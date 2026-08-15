# src/rune/commands/config.py
from pathlib import Path

import structlog
import typer

__all__ = ["config_cmd"]

logger = structlog.get_logger(__name__)


def config_cmd(
    key: str = typer.Argument(...),
    value: str | None = typer.Argument(None),
    add: bool = typer.Option(False, "--add", help="Add a new line to the option"),
    get_all: bool = typer.Option(False, "--get-all", help="Get all values"),
):
    """Get or set options in .rune/config"""
    from rune.config.exceptions import ValidationError
    from rune.schemas.config_schema import validate_config_key_value

    try:
        validate_config_key_value(key, value)
    except ValidationError as e:
        logger.error(str(e))
        raise typer.Exit(1)

    root_dir = Path.cwd()
    from rune.config.main import settings
    from rune.repositories import git_repository

    config_path = root_dir / ".rune" / "config"

    if value is not None and not config_path.exists():
        logger.error(".rune/config not found. Run `rune init` first.")
        raise typer.Exit(1)

    if value is None:
        if key == "agent.name":
            if get_all:
                values = git_repository.get_config_all(key, config_path)
                for v in values:
                    typer.echo(v)
            else:
                for a in settings.agent.names:
                    typer.echo(a)
        elif key == "submodule.path":
            if get_all:
                values = git_repository.get_config_all(key, config_path)
                for v in values:
                    typer.echo(v)
            else:
                for s in settings.submodule.paths:
                    typer.echo(s)
        elif key.startswith("remote.") and key.endswith(".url"):
            alias = key.split(".")[1]
            val = settings.remotes.get(alias)
            if val is not None:
                typer.echo(val)
            else:
                raise typer.Exit(1)
        elif key == "repomap.model":
            typer.echo(settings.repomap.model)
        elif key == "repomap.max-tokens":
            typer.echo(settings.repomap.max_tokens)
        else:
            if get_all:
                values = git_repository.get_config_all(key, config_path)
                for v in values:
                    typer.echo(v)
            else:
                val = git_repository.get_config(key, config_path)
                if val is not None:
                    typer.echo(val)
                else:
                    raise typer.Exit(1)
        return

    if key == "submodule.path":
        from rune.repositories import config_repository

        config_repository.add_submodule_path(root_dir, value)
    elif key == "agent.name":
        from rune.repositories import config_repository
        from rune.services import workspace_service

        config_repository.add_agent_name(root_dir, value)
        workspace_service.update_gitignore(root_dir)
    elif add:
        git_repository.add_config(key, value, config_path)
    else:
        git_repository.set_config(key, value, config_path)
