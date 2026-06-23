import typer
from rune.commands import rules, skills


def update_cmd(global_scope: bool = typer.Option(False, "--global", "-g")):
    """Update installed skills and rules."""
    typer.echo("Updating rules...")
    rules.update(global_scope=global_scope)

    typer.echo("\nUpdating skills...")
    skills.update(global_scope=global_scope)

    typer.echo("\nUpdated all modules.")
