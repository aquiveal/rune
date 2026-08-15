import os

from typer.testing import CliRunner

from rune.main import app

runner = CliRunner()


def test_config(tmp_path):
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])

    # Set
    result = runner.invoke(app, ["config", "agent.name", ".roo"])
    assert result.exit_code == 0

    # Additive Set
    result = runner.invoke(app, ["config", "agent.name", ".cursor"])
    assert result.exit_code == 0

    # Get
    result = runner.invoke(app, ["config", "agent.name", "--get-all"])
    assert result.exit_code == 0
    assert ".roo" in result.output
    assert ".cursor" in result.output


def test_config_submodule_additive(tmp_path):
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])

    # Set path 1
    res1 = runner.invoke(app, ["config", "submodule.path", "apps/frontend"])
    assert res1.exit_code == 0

    # Set path 2 (additive without --add)
    res2 = runner.invoke(app, ["config", "submodule.path", "apps/backend"])
    assert res2.exit_code == 0

    # Get all
    get_res = runner.invoke(app, ["config", "submodule.path", "--get-all"])
    assert get_res.exit_code == 0
    assert "apps/frontend" in get_res.output
    assert "apps/backend" in get_res.output
