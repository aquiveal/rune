import typer
from rune.commands import init, config, remote, status, update, skills, rules

app = typer.Typer(
    name="rune",
    help="Rune: The shadow version control system for LLM context.",
    add_completion=False,
    no_args_is_help=True,
)

@app.callback()
def callback():
    pass

# Base commands
app.command(name="init")(init.init_cmd)
app.command(name="config")(config.config_cmd)
app.command(name="status")(status.status_cmd)
app.command(name="update")(update.update_cmd)

# Sub-apps
app.add_typer(remote.app, name="remote")
app.add_typer(skills.app, name="skills")
app.add_typer(rules.app, name="rules")

def main():
    app()

if __name__ == "__main__":
    main()
