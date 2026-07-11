import typer
from rune.commands.init import init_cmd
from rune.commands.config import config_cmd
from rune.commands.status import status_cmd
from rune.commands.update import update_cmd
from rune.commands import remote, skills, rules, modules, agents

app = typer.Typer(
    name="rune",
    help="Rune: The shadow version control system for LLM context.",
    add_completion=False,
    no_args_is_help=True,
)


@app.callback()
def callback():
    from pathlib import Path
    from rune.repositories import git_repository
    from rune.services import workspace_service

    cwd = Path.cwd()
    git_root = git_repository.get_git_root(cwd)
    if git_root:
        if not workspace_service.is_initialized(git_root):
            workspace_service.init_workspace(git_root)
        workspace_service.update_gitignore(git_root)


# Base commands
app.command(name="init")(init_cmd)
app.command(name="config")(config_cmd)
app.command(name="status")(status_cmd)
app.command(name="update")(update_cmd)

# Sub-apps
app.add_typer(remote.app, name="remote")
app.add_typer(skills.app, name="skills")
app.add_typer(rules.app, name="rules")
app.add_typer(modules.app, name="modules")
app.add_typer(agents.app, name="agents")


def main():
    app()


if __name__ == "__main__":
    main()
