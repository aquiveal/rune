import typer
from typing import Optional
from pathlib import Path
from rune.repositories import config_repository
from rune.services import workspace_service

def config_cmd(
    key: str = typer.Argument(...),
    value: Optional[str] = typer.Argument(None),
    add: bool = typer.Option(False, "--add", help="Add a new line to the option"),
    get_all: bool = typer.Option(False, "--get-all", help="Get all values")
):
    """Get or set options in .rune/config"""
    root_dir = Path.cwd()
    from rune.repositories import git_repository
    from rune.config.main import RUNE_DIR, RUNE_CONFIG
    config_path = root_dir / RUNE_DIR / RUNE_CONFIG
    
    if not config_path.exists():
        typer.echo("Error: .rune/config not found. Run `rune init` first.", err=True)
        raise typer.Exit(1)
        
    if get_all:
        values = git_repository.get_config_all(key, config_path)
        for v in values: typer.echo(v)
        return
        
    if value is not None:
        if add: git_repository.add_config(key, value, config_path)
        else: git_repository.set_config(key, value, config_path)
            
        if key == "agent.name":
            workspace_service.update_gitignore(root_dir)
    else:
        val = git_repository.get_config(key, config_path)
        if val is not None: typer.echo(val)
        else: raise typer.Exit(1)
