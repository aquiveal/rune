from pathlib import Path
from typing import Annotated

import structlog
import typer

from rune.repositories import config_repository

__all__ = []

logger = structlog.get_logger(__name__)

app = typer.Typer(no_args_is_help=True, help="Manage remote repositories")


@app.command("add")
def add(
    name: Annotated[str, typer.Argument(help="Alias name for remote")],
    url: Annotated[str, typer.Argument(help="URL of remote repository")],
):
    """Add a new remote repository alias."""
    root_dir = Path.cwd()
    config_repository.set_remote_url(root_dir, name, url)
    logger.info(f"Added remote '{name}' -> {url}")
