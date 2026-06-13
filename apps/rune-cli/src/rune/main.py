import typer
from rune.commands import init, config, remote, status, update, skills, rules, submodule

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
    if git_root and workspace_service.is_initialized(git_root):
        workspace_service.update_gitignore(git_root)

# Base commands
app.command(name="init")(init.init_cmd)
app.command(name="config")(config.config_cmd)
app.command(name="status")(status.status_cmd)
app.command(name="update")(update.update_cmd)

# Sub-apps
app.add_typer(remote.app, name="remote")
app.add_typer(skills.app, name="skills")
app.add_typer(rules.app, name="rules")
app.add_typer(submodule.app, name="submodule")

def main():
    app()

if __name__ == "__main__":
    main()
