import typer
from pathlib import Path
from rune.services import workspace_service

def init_cmd():
    """Initialize a new Rune repository."""
    cwd = Path.cwd()
    if workspace_service.is_initialized(cwd):
        typer.echo("Rune is already initialized in this directory.")
        return

    workspace_service.init_workspace(cwd)
    typer.echo("Initialized empty Rune repository")
