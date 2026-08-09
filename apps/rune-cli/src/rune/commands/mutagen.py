from pathlib import Path
from typing import Annotated

import structlog
import typer

from rune.config.exceptions import RuneError
from rune.repositories import git_repository
from rune.services import mutagen_service

__all__ = ["app", "update"]

app = typer.Typer(
    no_args_is_help=True, help="Manage Mutagen integration and sync configurations."
)
logger = structlog.get_logger(__name__)


@app.command("update")
def update(
    gitignore_path: Annotated[
        Path | None,
        typer.Option("--gitignore", "-g", help="Custom path to .gitignore file"),
    ] = None,
    mutagen_path: Annotated[
        Path | None,
        typer.Option("--mutagen", "-m", help="Custom path to mutagen.yml file"),
    ] = None,
):
    """Copy .gitignore ignore patterns into mutagen.yml defaults ignore list."""
    cwd = Path.cwd()
    git_root = git_repository.get_git_root(cwd) or cwd

    try:
        target_file, added = mutagen_service.update_mutagen_ignore(
            git_root=git_root,
            gitignore_path=gitignore_path,
            mutagen_path=mutagen_path,
        )
        logger.info(
            f"Successfully updated '{target_file.name}' defaults ignore list: "
            f"added {added} new ignore pattern(s)."
        )
    except RuneError as e:
        logger.error(str(e))
        raise typer.Exit(1)
