import typer
from pathlib import Path


def diff_cmd():
    """
    Show changes between agent rules and upstream. (Placeholder)
    """
    cwd = Path.cwd()
    if not (cwd / ".rune").exists():
        typer.echo("Error: .rune directory not found. Run `rune init` first.", err=True)
        raise typer.Exit(1)

    typer.echo("No local changes.")
