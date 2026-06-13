import pytest
from typer.testing import CliRunner
from rune.main import app
import os

runner = CliRunner()

def test_rules_add(tmp_path, mock_git_repo):
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])
    
    repo_url = str(mock_git_repo).replace('\\', '/')
    result = runner.invoke(app, ["rules", "add", repo_url, "--agent", ".roo"])
    
    assert result.exit_code == 0
    assert "Installed rule 'test-rule'" in result.stdout
    assert (tmp_path / ".roo" / "rules" / "test-rule").exists()
