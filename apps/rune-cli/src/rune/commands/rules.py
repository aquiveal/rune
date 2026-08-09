from pathlib import Path
from typing import Annotated

import questionary
import structlog
import typer

from rune.config.exceptions import RuneError
from rune.repositories import git_repository
from rune.services import module_service, rule_service, workspace_service
from rune.utils.url import parse_github_url, resolve_url

__all__ = []

app = typer.Typer(no_args_is_help=True, help="Manage agent context and guidelines")
logger = structlog.get_logger(__name__)


@app.command("add")
def add(
    source: Annotated[
        str, typer.Argument(help="Source URL, owner/repo, or remote alias")
    ],
    agents: Annotated[
        list[str] | None,
        typer.Option("--agent", "-a", help="Target agents"),
    ] = None,
    rules: Annotated[
        list[str] | None,
        typer.Option("--rule", "-r", help="Specific rules to install"),
    ] = None,
    global_scope: Annotated[
        bool, typer.Option("--global", "-g", help="Install globally")
    ] = False,
    copy_mode: Annotated[
        bool, typer.Option("--copy", help="Copy instead of symlink")
    ] = False,
):
    """Install rules from a repository."""
    cwd = Path.cwd()
    git_root = git_repository.get_git_root(cwd)

    if not global_scope and not git_root:
        logger.error("Must be run inside a git repository.")
        raise typer.Exit(1)

    raw_url = resolve_url(source, git_root or cwd)
    url, extracted_path = parse_github_url(raw_url)

    import shutil
    import uuid

    tmp_dir = (git_root or cwd) / ".rune" / "tmp" / str(uuid.uuid4())
    tmp_dir.mkdir(parents=True, exist_ok=True)

    try:
        git_repository.clone(url, tmp_dir, depth=1)
        discovered = rule_service.discover_rules(tmp_dir)

        if not discovered:
            logger.error("No rules found in repository.")
            raise typer.Exit(1)

        to_install = []
        if rules:
            to_install = [
                r
                for r in discovered
                if r.name in rules or r.name.replace(".md", "") in rules
            ]
            if not to_install:
                logger.error(f"No rules found matching: {', '.join(rules)}")
                raise typer.Exit(1)
        elif extracted_path:
            # If a specific path was provided in the URL, try to find a rule matching that path
            to_install = [
                r
                for r in discovered
                if r.path == extracted_path
                or (r.path and r.path.startswith(extracted_path + "/"))
            ]
            if not to_install:
                logger.error(f"No rules found at path '{extracted_path}'.")
                raise typer.Exit(1)
        elif len(discovered) == 1:
            to_install = discovered
        else:
            choices = [r.name for r in discovered]
            selected = questionary.checkbox(
                "Select rules to install:", choices=choices
            ).ask()
            if not selected:
                return
            to_install = [r for r in discovered if r.name in selected]

        target_agents = workspace_service.resolve_target_agents(
            git_root=git_root,
            cwd=cwd,
            global_scope=global_scope,
            agents_arg=agents,
        )
        if target_agents is None:
            return

        for rule in to_install:
            module_service.add_module(
                git_root=git_root or cwd,
                cwd=cwd,
                url=url,
                path=rule.path or ".",
                name=rule.name,
                type="rules",
                agents=target_agents,
                global_scope=global_scope,
                copy_mode=copy_mode,
            )
            if target_agents:
                logger.info(
                    f"Installed rule '{rule.name}' to {', '.join(target_agents)}"
                )
            else:
                logger.info(f"Installed rule '{rule.name}' to {cwd}")

        # Merge rules into AGENTS.md after adding
        try:
            rule_service.merge_rules_to_agents_md(git_root or cwd)
            logger.info("Successfully merged rules into AGENTS.md")
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to merge rules: {e}")

    except RuneError as e:
        logger.error(str(e))
        raise typer.Exit(1)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


@app.command("list")
def list_rules(
    global_scope: Annotated[bool, typer.Option("--global", "-g")] = False,
):
    """List installed rules."""
    cwd = Path.cwd()
    git_root = git_repository.get_git_root(cwd) or cwd
    status = module_service.get_status(git_root, global_scope=global_scope)
    for mod, stat in status.items():
        if "/rules/" in mod or mod.startswith("rules/"):
            logger.info(f"{mod}: {stat}")


@app.command("remove")
def remove(
    names: Annotated[list[str], typer.Argument(help="Names of rules to remove")],
    global_scope: Annotated[bool, typer.Option("--global", "-g")] = False,
):
    """Remove installed rules."""
    cwd = Path.cwd()
    git_root = git_repository.get_git_root(cwd) or cwd
    for name in names:
        module_service.remove_module(git_root, name, "rules", global_scope=global_scope)
        logger.info(f"Removed rule '{name}'")


@app.command("update")
def update(
    global_scope: Annotated[bool, typer.Option("--global", "-g")] = False,
):
    """Update installed rules and merge them into AGENTS.md."""
    cwd = Path.cwd()
    git_root = git_repository.get_git_root(cwd) or cwd

    try:
        module_service.update_modules(git_root, type="rules", global_scope=global_scope)
        logger.info("Updated installed rule submodules.")
    except Exception as e:  # noqa: BLE001
        logger.error(f"Failed to update rule submodules: {e}")

    # Also update any nested submodules inside rule directories (for authors)
    rule_dirs = rule_service.discover_rule_dirs(git_root)
    if rule_dirs:
        for rule_dir in rule_dirs:
            try:
                if (rule_dir / ".git").exists():
                    git_repository.update_submodules(rule_dir)
                    logger.info(f"Updated nested submodules in {rule_dir}")
            except Exception as e:  # noqa: BLE001
                logger.error(f"Failed to update nested submodules in {rule_dir}: {e}")

    try:
        rule_service.merge_rules_to_agents_md(git_root)
        logger.info("Successfully merged rules into AGENTS.md")
    except Exception as e:  # noqa: BLE001
        logger.error(f"Failed to merge rules: {e}")
        raise typer.Exit(1)


@app.command("init")
def init(
    name: Annotated[str, typer.Argument(help="Name of the rule")],
):
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
        "type-safety.md",
    ]

    for file in files:
        (rule_dir / file).touch(exist_ok=True)

    logger.info(f"Created rule '{name}' with standard files at {rule_dir}")
