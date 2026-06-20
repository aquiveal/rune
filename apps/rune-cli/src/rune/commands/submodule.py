import typer
from typing import Optional
from pathlib import Path
from rune.commands import skills
from rune.repositories import git_repository
from rune.services import skill_service

app = typer.Typer(no_args_is_help=True, help="Manage submodules contextually")

@app.command("add")
def add(
    url: str = typer.Argument(..., help="URL of the git repository to add as a submodule"),
    target_name: Optional[str] = typer.Argument(None, help="Name of the skill/rule to add the submodule to"),
    force: bool = typer.Option(False, "--force", "-f", help="Force add the submodule")
):
    """Add a submodule contextually based on the current directory."""
    cwd = Path.cwd()
    
    # Extract repo name from URL
    repo_name = url.rstrip('/').split('/')[-1]
    if repo_name.endswith('.git'):
        repo_name = repo_name[:-4]
        
    target_dir = None
    context = None
    
    # Determine context
    if cwd.name == "skills":
        context = "skills_root"
        raw_name = target_name or repo_name
        sanitized_name = skill_service.sanitize_skill_name(raw_name)
        if not sanitized_name:
            typer.echo(f"Error: Invalid skill name '{raw_name}'.", err=True)
            raise typer.Exit(1)
        target_dir = cwd / sanitized_name
    elif cwd.parent.name == "skills":
        context = "inside_skill"
        target_dir = cwd
    else:
        typer.echo("Error: You must be inside a 'skills' directory to use this command.", err=True)
        raise typer.Exit(1)
        
    try:
        # Scaffold if necessary
        if context == "skills_root" and not target_dir.exists():
            typer.echo(f"Scaffolding new skill '{target_dir.name}'...")
            skills.scaffold_skill(target_dir.name, cwd)
            
        # Ensure modules directory exists
        modules_dir = target_dir / "modules"
        modules_dir.mkdir(exist_ok=True)
        
        submodule_path = f"modules/{repo_name}"
        
        from rune.services import module_service
        
        typer.echo(f"Adding submodule {url} to {submodule_path}...")
        git_root = git_repository.get_git_root(cwd) or cwd
        
        try:
            module_service.add_module(
                git_root=git_root,
                cwd=target_dir,
                url=url,
                path=".",
                name=repo_name,
                type="modules",
                agents=[],
                global_scope=False,
                copy_mode=False
            )
        except Exception as e:
            raise Exception(f"Failed to fetch submodule: {e}")
        
        typer.echo("Syncing skill tree...")
        skill_service.update_skill_tree(target_dir)
        
        typer.echo(f"Successfully added submodule and updated skill '{target_dir.name}'")
        
    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"Failed to add submodule: {e}", err=True)
        raise typer.Exit(1)
