import typer
import questionary
from typing import List, Optional
from pathlib import Path
import structlog
from rune.services import skill_service, module_service, workspace_service
from rune.repositories import git_repository
from rune.config.exceptions import RuneError, ValidationError
from rune.utils.url import parse_github_url, resolve_url

app = typer.Typer(no_args_is_help=True, help="Manage executable agent skills")
logger = structlog.get_logger(__name__)


@app.command("add")
def add(
    source: str = typer.Argument(..., help="Source URL, owner/repo, or remote alias"),
    agents: Optional[List[str]] = typer.Option(
        None, "--agent", "-a", help="Target agents"
    ),
    skills: Optional[List[str]] = typer.Option(
        None, "--skill", "-s", help="Specific skills to install"
    ),
    global_scope: bool = typer.Option(False, "--global", "-g", help="Install globally"),
    copy_mode: bool = typer.Option(False, "--copy", help="Copy instead of symlink"),
):
    """Install skills from a repository."""
    cwd = Path.cwd()
    git_root = git_repository.get_git_root(cwd)

    if not global_scope and not git_root:
        logger.error("Must be run inside a git repository.")
        raise typer.Exit(1)

    raw_url = resolve_url(source, git_root or cwd)
    url, extracted_path = parse_github_url(raw_url)

    # Temp clone for discovery
    import uuid
    import shutil

    tmp_dir = (git_root or cwd) / ".rune" / "tmp" / str(uuid.uuid4())
    tmp_dir.mkdir(parents=True, exist_ok=True)

    try:
        git_repository.clone(url, tmp_dir, depth=1)
        discovered = skill_service.discover_skills(tmp_dir)

        if not discovered:
            logger.error("No skills found in repository.")
            raise typer.Exit(1)

        # Filter or prompt
        to_install = []
        if skills:
            to_install = [
                s
                for s in discovered
                if s.name in skills or s.name.replace(".md", "") in skills
            ]
            if not to_install:
                logger.error(f"No skills found matching: {', '.join(skills)}")
                raise typer.Exit(1)
        elif extracted_path:
            to_install = [
                s
                for s in discovered
                if s.path == extracted_path
                or (s.path and s.path.startswith(extracted_path + "/"))
            ]
            if not to_install:
                logger.error(f"No skills found at path '{extracted_path}'.")
                raise typer.Exit(1)
        elif len(discovered) == 1:
            to_install = discovered
        else:
            choices = [s.name for s in discovered]
            selected = questionary.checkbox(
                "Select skills to install:", choices=choices
            ).ask()
            if not selected:
                return
            to_install = [s for s in discovered if s.name in selected]

        # Detect agents
        target_agents = workspace_service.resolve_target_agents(
            git_root=git_root,
            cwd=cwd,
            global_scope=global_scope,
            agents_arg=agents,
        )
        if target_agents is None:
            return

        for skill in to_install:
            module_service.add_module(
                git_root=git_root or cwd,
                cwd=cwd,
                url=url,
                path=skill.path or ".",
                name=skill.name,
                type="skills",
                agents=target_agents,
                global_scope=global_scope,
                copy_mode=copy_mode,
            )
            if target_agents:
                logger.info(
                    f"Installed skill '{skill.name}' to {', '.join(target_agents)}"
                )
            else:
                logger.info(f"Installed skill '{skill.name}' to {cwd}")

    except RuneError as e:
        logger.error(str(e))
        raise typer.Exit(1)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


@app.command("list")
def list_skills(global_scope: bool = typer.Option(False, "--global", "-g")):
    """List installed skills."""
    cwd = Path.cwd()
    git_root = git_repository.get_git_root(cwd) or cwd
    status = module_service.get_status(git_root, global_scope=global_scope)
    for mod, stat in status.items():
        if "/skills/" in mod or mod.startswith("skills/"):
            logger.info(f"{mod}: {stat}")


@app.command("remove")
def remove(
    names: List[str] = typer.Argument(..., help="Names of skills to remove"),
    global_scope: bool = typer.Option(False, "--global", "-g"),
):
    """Remove installed skills."""
    cwd = Path.cwd()
    git_root = git_repository.get_git_root(cwd) or cwd
    for name in names:
        module_service.remove_module(
            git_root, name, "skills", global_scope=global_scope
        )
        logger.info(f"Removed skill '{name}'")


def scaffold_skill(name: str, base_dir: Path) -> Path:
    """Scaffold a new skill with standard folder structure."""
    skill_dir = base_dir / name
    skill_dir.mkdir(exist_ok=True)

    # Create standard directories
    (skill_dir / "scripts").mkdir(exist_ok=True)
    (skill_dir / "references").mkdir(exist_ok=True)
    (skill_dir / "assets").mkdir(exist_ok=True)
    (skill_dir / "modules").mkdir(exist_ok=True)

    # Create SKILL.md
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        description = f"Provides specialized context, rules, and tools for implementing, configuring, and debugging {name}. Use this skill whenever modifying {name} configurations or adding related functionality."
        skill_md.write_text(
            f"---\nname: {name}\ndescription: {description}\n---\n# {name}\n"
        )

    return skill_dir


@app.command("init")
def init(name: str = typer.Argument(..., help="Name of the skill")):
    """Scaffold a new skill with standard folder structure."""
    sanitized_name = skill_service.sanitize_skill_name(name)
    if not sanitized_name:
        logger.error(f"Invalid skill name '{name}'.")
        raise typer.Exit(1)

    skill_dir = scaffold_skill(sanitized_name, Path.cwd())
    logger.info(
        f"Created skill '{sanitized_name}' with standard structure at {skill_dir}"
    )


@app.command("update")
def update(global_scope: bool = typer.Option(False, "--global", "-g")):
    """Update installed skills and sync SKILL.md for skills in the current context."""
    cwd = Path.cwd()
    git_root = git_repository.get_git_root(cwd) or cwd

    try:
        module_service.update_modules(
            git_root, type="skills", global_scope=global_scope
        )
        module_service.update_modules(
            git_root, type="modules", global_scope=global_scope
        )
        logger.info("Updated installed skills and their internal submodules.")
    except Exception as e:
        logger.error(f"Failed to update skill submodules: {e}")

    discovered = skill_service.discover_skills(git_root)

    if not discovered:
        logger.error("No skills found in the current context to compile.")
        return

    updated_count = 0
    for skill in discovered:
        skill_dir = (git_root / skill.path).resolve() if skill.path else git_root

        try:
            # Update SKILL.md tree
            skill_service.update_skill_tree(skill_dir)

            updated_count += 1
            logger.info(f"Updated SKILL.md for '{skill.name}' at {skill_dir}")
        except Exception as e:
            logger.error(f"Failed to update skill '{skill.name}': {e}")

    logger.info(f"Successfully compiled {updated_count} skill(s).")


@app.command("validate")
def validate(
    path: Path = typer.Argument(
        Path.cwd(), help="Path to the skill directory or SKILL.md"
    ),
):
    """Validate a skill's metadata against the specification."""
    if path.is_dir():
        skill_file = path / "SKILL.md"
    else:
        skill_file = path

    try:
        skill = skill_service.validate_skill_file(skill_file)
        logger.info(f"Skill '{skill.name}' is valid!")
    except ValidationError as e:
        logger.error(f"Validation failed: {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise typer.Exit(1)
