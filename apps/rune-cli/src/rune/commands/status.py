import typer
from pathlib import Path
from rune.services import module_service

def status_cmd():
    """Show status of installed skills and rules."""
    cwd = Path.cwd()
    status = module_service.get_status(cwd)
    for mod, stat in status.items():
        typer.echo(f"{mod}: {stat}")
