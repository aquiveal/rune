import typer
from pathlib import Path
from worldline import structlog
from rune.repositories import git_repository
from rune.services import rule_service, module_service, skill_service, map_service

app = typer.Typer(no_args_is_help=True, help="Manage agents context, rules, skills, and map.")
logger = structlog.get_logger(__name__)

@app.command("update")
def update(global_scope: bool = typer.Option(False, "--global", "-g")):
    """Update all agent contexts (rules, skills, modules) and merge repository map."""
    cwd = Path.cwd()
    git_root = git_repository.get_git_root(cwd) or cwd

    # Step 1: Rules
    try:
        module_service.update_modules(git_root, type="rules", global_scope=global_scope)
        rule_dirs = rule_service.discover_rule_dirs(git_root)
        if rule_dirs:
            for rule_dir in rule_dirs:
                if (rule_dir / ".git").exists():
                    git_repository.update_submodules(rule_dir)
        logger.info("Successfully updated rules.")
        typer.echo("Successfully updated rules.")
    except Exception as e:
        logger.exception("Failed to update rules.")

    # Step 2: Skills and their ASTs
    try:
        module_service.update_modules(git_root, type="skills", global_scope=global_scope)
        module_service.update_modules(git_root, type="modules", global_scope=global_scope)
        skills = skill_service.discover_skills(git_root)
        if skills:
            for skill in skills:
                skill_dir = git_root / skill.path if skill.path else git_root
                skill_service.update_skill_tree(skill_dir)
        logger.info("Successfully updated skills and their ASTs.")
        typer.echo("Successfully updated skills and their ASTs.")
    except Exception as e:
        logger.exception("Failed to update skills and their ASTs.")

    # Step 3: Merge Rules
    try:
        rule_service.merge_rules_to_agents_md(git_root)
        logger.info("Successfully merged rules into AGENTS.md.")
        typer.echo("Successfully merged rules into AGENTS.md.")
    except Exception as e:
        logger.exception("Failed to merge rules into AGENTS.md.")

    # Step 4: Generate Repo AST and Merge
    try:
        typer.echo("Generating full repository AST map...")
        logger.info("Generating full repository AST map...")
        repo_ast = map_service.generate_submodule_map(git_root)
        map_service.merge_ast_to_agents_md(git_root, repo_ast)
        logger.info("Successfully generated and merged repo AST map.")
        typer.echo("Successfully generated and merged repo AST map.")
    except Exception as e:
        logger.exception("Failed to generate and merge repo AST map.")
