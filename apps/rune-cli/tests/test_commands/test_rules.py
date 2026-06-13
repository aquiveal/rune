import pytest
from typer.testing import CliRunner
from rune.main import app
import os

runner = CliRunner()

def test_rules_add(tmp_path, mock_git_repo):
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])
    
    # Initialize git repo for submodules
    import subprocess
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)
    
    repo_url = "file:///" + str(mock_git_repo).replace('\\', '/')
    result = runner.invoke(app, ["rules", "add", repo_url, "--agent", ".roo"])
    
    if result.exit_code != 0:
        print(result.output)
        if result.exception:
            print(result.exception)
            
    assert result.exit_code == 0
    assert "Installed rule 'test-rule'" in result.stdout
    assert (tmp_path / ".roo" / "rules" / "test-rule").exists()

def test_rules_update(tmp_path):
    os.chdir(tmp_path)
    
    # Create a mock rule directory
    rule_dir = tmp_path / ".roo" / "rules" / "my-rule"
    rule_dir.mkdir(parents=True)
    (rule_dir / "test.md").write_text("Test rule content")
    
    result = runner.invoke(app, ["rules", "update"])
    assert result.exit_code == 0
    
    agents_md = tmp_path / "AGENTS.md"
    assert agents_md.exists()
    content = agents_md.read_text()
    assert "## my-rule" in content
    assert "Test rule content" in content
    assert "Test rule content" in content
