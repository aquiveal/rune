import typer
from pathlib import Path
from rune.services import module_service

def update_cmd(global_scope: bool = typer.Option(False, "--global", "-g")):
    """Update installed skills and rules."""
    module_service.update_modules(Path.cwd(), global_scope=global_scope)
    typer.echo("Updated all modules.")
