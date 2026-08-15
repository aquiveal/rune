import os

from typer.testing import CliRunner

from rune.main import app

runner = CliRunner()


def test_cli_config_invalid_key(tmp_path):
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])

    result = runner.invoke(app, ["config", "invalid.key.name", "foo"])
    assert result.exit_code != 0


def test_cli_config_submodule_path(tmp_path):
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])

    result = runner.invoke(
        app, ["config", "submodule.path", "submodules/frontend", "--add"]
    )
    assert result.exit_code == 0
