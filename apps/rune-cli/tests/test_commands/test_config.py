import pytest
from typer.testing import CliRunner
from rune.main import app
import os

runner = CliRunner()

def test_config(tmp_path):
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])
    
    # Set
    result = runner.invoke(app, ["config", "agent.name", ".roo"])
    assert result.exit_code == 0
    
    # Get
    result = runner.invoke(app, ["config", "agent.name"])
    assert result.exit_code == 0
    assert ".roo" in result.stdout
