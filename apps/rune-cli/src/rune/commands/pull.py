from pathlib import Path

import structlog
import typer

from rune.services import module_service

__all__ = ["pull_cmd"]

logger = structlog.get_logger(__name__)


def pull_cmd():
    """
    Pull and merge updates for runemodules.
    """
    cwd = Path.cwd()
    if not (cwd / ".rune").exists():
        logger.error(".rune directory not found. Run `rune init` first.")
        raise typer.Exit(1)

    logger.info("Pulling modules...")
    module_service.update_modules(cwd)
    logger.info("Pull complete.")
