import typer
import questionary
from typing import List, Optional
from pathlib import Path
from rune.services import rule_service, module_service, workspace_service
from rune.repositories import config_repository, git_repository
from rune.config.exceptions import RuneError

app = typer.Typer(no_args_is_help=True, help="Manage agent context and guidelines")

def resolve_url(source: str, root_dir: Path) -> str:
    if Path(source).exists():
        return str(Path(source).absolute())
    url = config_repository.get_remote_url(root_dir, source)
    if url: return url
    if "/" in source and not source.startswith(("http://", "https://", "git@")):
        return f"https://github.com/{source}.git"
    return source

@app.command("add")
def add(
    source: str = typer.Argument(..., help="Source URL, owner/repo, or remote alias"),
    agents: Optional[List[str]] = typer.Option(None, "--agent", "-a", help="Target agents"),
    rules: Optional[List[str]] = typer.Option(None, "--rule", "-r", help="Specific rules to install"),
    global_scope: bool = typer.Option(False, "--global", "-g", help="Install globally"),
    copy_mode: bool = typer.Option(False, "--copy", help="Copy instead of symlink")
):
    """Install rules from a repository."""
    root_dir = Path.cwd()
    url = resolve_url(source, root_dir)
    
    import uuid
    import shutil
    tmp_dir = root_dir / ".rune" / "tmp" / str(uuid.uuid4())
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        git_repository.clone(url, tmp_dir, depth=1)
        discovered = rule_service.discover_rules(tmp_dir)
        
        if not discovered:
            typer.echo("No rules found in repository.", err=True)
            raise typer.Exit(1)
            
        to_install = []
        if rules:
            to_install = [r for r in discovered if r.name in rules]
        elif len(discovered) == 1:
            to_install = discovered
        else:
            choices = [r.name for r in discovered]
            selected = questionary.checkbox("Select rules to install:", choices=choices).ask()
            if not selected: return
            to_install = [r for r in discovered if r.name in selected]
            
        target_agents = agents or workspace_service.detect_agents(root_dir)
        if not target_agents:
            target_agents = questionary.checkbox("Select target agents:", choices=[".roo", ".claude", ".cursor", ".cline"]).ask()
            if not target_agents: return

        for rule in to_install:
            module_service.add_module(
                root_dir=root_dir,
                url=url,
                path=rule.path,
                name=rule.name,
                type="rules",
                agents=target_agents,
                global_scope=global_scope,
                copy_mode=copy_mode
            )
            typer.echo(f"Installed rule '{rule.name}' to {', '.join(target_agents)}")
            
    except RuneError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.command("develop")
def develop(url: str = typer.Argument(..., help="URL of the rules repository")):
    """Add rules as a git submodule for local development."""
    try:
        module_service.add_git_submodule(Path.cwd(), url, target_dir="rules")
        typer.echo(f"Added rules submodule for development.")
    except RuneError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

@app.command("list")
def list_rules(global_scope: bool = typer.Option(False, "--global", "-g")):
    """List installed rules."""
    status = module_service.get_status(Path.cwd(), global_scope=global_scope)
    for mod, stat in status.items():
        if mod.startswith("rules/"):
            typer.echo(f"{mod}: {stat}")

@app.command("remove")
def remove(
    names: List[str] = typer.Argument(..., help="Names of rules to remove"),
    global_scope: bool = typer.Option(False, "--global", "-g")
):
    """Remove installed rules."""
    for name in names:
        module_service.remove_module(Path.cwd(), name, "rules", global_scope=global_scope)
        typer.echo(f"Removed rule '{name}'")

@app.command("update")
def update():
    """Update submodules for rules and merge them into AGENTS.md."""
    root_dir = Path.cwd()
    rule_dirs = rule_service.discover_rule_dirs(root_dir)
    
    if not rule_dirs:
        typer.echo("No rule directories found.", err=True)
        raise typer.Exit(1)
        
    for rule_dir in rule_dirs:
        try:
            git_repository.update_submodules(rule_dir)
            typer.echo(f"Updated submodules in {rule_dir}")
        except Exception as e:
            typer.echo(f"Failed to update submodules in {rule_dir}: {e}", err=True)
            
    try:
        rule_service.merge_rules_to_agents_md(root_dir)
        typer.echo(f"Successfully merged rules into AGENTS.md")
    except Exception as e:
        typer.echo(f"Failed to merge rules: {e}", err=True)
        raise typer.Exit(1)

@app.command("init")
def init(name: str = typer.Argument(..., help="Name of the rule")):
    """Scaffold a new rule with standard markdown files."""
    rule_dir = Path.cwd() / name
    rule_dir.mkdir(exist_ok=True)
    
    files = [
        "anti-patterns.md",
        "architecture-and-structure.md",
        "code-style-and-formatting.md",
        "configuration-and-environment.md",
        "dependency-management.md",
        "documentation-and-comments.md",
        "error-handling.md",
        "logging-and-observability.md",
        "naming-conventions.md",
        "performance-and-optimization.md",
        "security-and-validation.md",
        "testing-standards.md",
        "type-safety.md"
    ]
    
    for file in files:
        (rule_dir / file).touch(exist_ok=True)
        
    typer.echo(f"Created rule '{name}' with standard files at {rule_dir}")
