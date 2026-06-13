import typer
import questionary
from typing import List, Optional
from pathlib import Path
from rune.services import skill_service, module_service, workspace_service
from rune.repositories import config_repository, git_repository
from rune.config.exceptions import RuneError, ValidationError

app = typer.Typer(no_args_is_help=True, help="Manage executable agent skills")

def resolve_url(source: str, root_dir: Path) -> str:
    # 1. Check if it's a local path
    if Path(source).exists():
        return str(Path(source).absolute())

    # 2. Check remote config
    url = config_repository.get_remote_url(root_dir, source)
    if url:
        return url
    
    # 3. Check if it's owner/repo
    if "/" in source and not source.startswith(("http://", "https://", "git@")):
        return f"https://github.com/{source}.git"
    
    return source

@app.command("add")
def add(
    source: str = typer.Argument(..., help="Source URL, owner/repo, or remote alias"),
    agents: Optional[List[str]] = typer.Option(None, "--agent", "-a", help="Target agents"),
    skills: Optional[List[str]] = typer.Option(None, "--skill", "-s", help="Specific skills to install"),
    global_scope: bool = typer.Option(False, "--global", "-g", help="Install globally"),
    copy_mode: bool = typer.Option(False, "--copy", help="Copy instead of symlink")
):
    """Install skills from a repository."""
    root_dir = Path.cwd()
    url = resolve_url(source, root_dir)
    
    # Temp clone for discovery
    import uuid
    import shutil
    tmp_dir = root_dir / ".rune" / "tmp" / str(uuid.uuid4())
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        git_repository.clone(url, tmp_dir, depth=1)
        discovered = skill_service.discover_skills(tmp_dir)
        
        if not discovered:
            typer.echo("No skills found in repository.", err=True)
            raise typer.Exit(1)
            
        # Filter or prompt
        to_install = []
        if skills:
            to_install = [s for s in discovered if s.name in skills]
        elif len(discovered) == 1:
            to_install = discovered
        else:
            choices = [s.name for s in discovered]
            selected = questionary.checkbox("Select skills to install:", choices=choices).ask()
            if not selected:
                return
            to_install = [s for s in discovered if s.name in selected]
            
        # Detect agents
        target_agents = agents or workspace_service.detect_agents(root_dir)
        if not target_agents:
            target_agents = questionary.checkbox("Select target agents:", choices=[".roo", ".claude", ".cursor", ".cline"]).ask()
            if not target_agents:
                return

        for skill in to_install:
            module_service.add_module(
                root_dir=root_dir,
                url=url,
                path=skill.path,
                name=skill.name,
                type="skills",
                agents=target_agents,
                global_scope=global_scope,
                copy_mode=copy_mode
            )
            typer.echo(f"Installed skill '{skill.name}' to {', '.join(target_agents)}")
            
    except RuneError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.command("develop")
def develop(url: str = typer.Argument(..., help="URL of the skill repository")):
    """Add a skill as a git submodule for local development."""
    try:
        module_service.add_git_submodule(Path.cwd(), url, target_dir="skills")
        typer.echo(f"Added skill submodule for development.")
    except RuneError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

@app.command("list")
def list_skills(global_scope: bool = typer.Option(False, "--global", "-g")):
    """List installed skills."""
    status = module_service.get_status(Path.cwd(), global_scope=global_scope)
    for mod, stat in status.items():
        if mod.startswith("skills/"):
            typer.echo(f"{mod}: {stat}")

@app.command("remove")
def remove(
    names: List[str] = typer.Argument(..., help="Names of skills to remove"),
    global_scope: bool = typer.Option(False, "--global", "-g")
):
    """Remove installed skills."""
    for name in names:
        module_service.remove_module(Path.cwd(), name, "skills", global_scope=global_scope)
        typer.echo(f"Removed skill '{name}'")

@app.command("init")
def init(name: str = typer.Argument(..., help="Name of the skill")):
    """Scaffold a new skill with standard folder structure."""
    skill_dir = Path.cwd() / name
    skill_dir.mkdir(exist_ok=True)
    
    # Create standard directories
    (skill_dir / "scripts").mkdir(exist_ok=True)
    (skill_dir / "references").mkdir(exist_ok=True)
    (skill_dir / "assets").mkdir(exist_ok=True)
    
    # Create SKILL.md
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        skill_md.write_text(f"---\nname: {name}\ndescription: {name} skill\n---\n# {name}\n")
    
    typer.echo(f"Created skill '{name}' with standard structure at {skill_dir}")

@app.command("validate")
def validate(path: Path = typer.Argument(Path.cwd(), help="Path to the skill directory or SKILL.md")):
    """Validate a skill's metadata against the specification."""
    if path.is_dir():
        skill_file = path / "SKILL.md"
    else:
        skill_file = path
        
    try:
        skill = skill_service.validate_skill_file(skill_file)
        typer.echo(f"Skill '{skill.name}' is valid!")
    except ValidationError as e:
        typer.echo(f"Validation failed: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"An unexpected error occurred: {e}", err=True)
        raise typer.Exit(1)
