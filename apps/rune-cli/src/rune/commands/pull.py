import typer
from pathlib import Path
from rune.services import module_service


def pull_cmd():
    """
    Pull and merge updates for runemodules.
    """
    cwd = Path.cwd()
    if not (cwd / ".rune").exists():
        typer.echo("Error: .rune directory not found. Run `rune init` first.", err=True)
        raise typer.Exit(1)

    typer.echo("Pulling modules...")
    module_service.update_modules(cwd)
    typer.echo("Pull complete.")
