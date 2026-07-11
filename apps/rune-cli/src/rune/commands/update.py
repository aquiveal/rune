import typer
import structlog
from rune.commands import rules, skills

logger = structlog.get_logger(__name__)


def update_cmd(global_scope: bool = typer.Option(False, "--global", "-g")):
    """Update installed skills and rules."""
    logger.info("Updating rules...")
    rules.update(global_scope=global_scope)

    logger.info("Updating skills...")
    skills.update(global_scope=global_scope)

    logger.info("Updated all modules.")
