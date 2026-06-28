import typer
from pathlib import Path
from worldline import structlog
from rune.repositories import config_repository

logger = structlog.get_logger(__name__)

app = typer.Typer(no_args_is_help=True, help="Manage remote repositories")


@app.command("add")
def add(name: str = typer.Argument(...), url: str = typer.Argument(...)):
    """Add a new remote repository alias."""
    root_dir = Path.cwd()
    config_repository.set_remote_url(root_dir, name, url)
    logger.info(f"Added remote '{name}' -> {url}")
