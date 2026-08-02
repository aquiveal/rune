from pathlib import Path
import structlog
from rune.services import module_service

logger = structlog.get_logger(__name__)


def status_cmd():
    """Show status of installed skills and rules."""
    cwd = Path.cwd()
    status = module_service.get_status(cwd)
    for mod, stat in status.items():
        logger.info(f"{mod}: {stat}")
