import typer
from pathlib import Path
import structlog
from rune.services import workspace_service

logger = structlog.get_logger(__name__)


def init_cmd():
    """Initialize a new Rune repository."""
    cwd = Path.cwd()
    if workspace_service.is_initialized(cwd):
        logger.info("Rune is already initialized in this directory.")
        return

    workspace_service.init_workspace(cwd)
    logger.info("Initialized empty Rune repository")
