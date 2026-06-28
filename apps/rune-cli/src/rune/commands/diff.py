import typer
from pathlib import Path
from worldline import structlog

logger = structlog.get_logger(__name__)


def diff_cmd():
    """
    Show changes between agent rules and upstream. (Placeholder)
    """
    cwd = Path.cwd()
    if not (cwd / ".rune").exists():
        logger.error(".rune directory not found. Run `rune init` first.")
        raise typer.Exit(1)

    logger.info("No local changes.")
