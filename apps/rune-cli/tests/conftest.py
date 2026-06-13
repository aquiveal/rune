import pytest
from pathlib import Path
import subprocess
import os

@pytest.fixture
def mock_git_repo(tmp_path):
    repo_path = tmp_path / "mock_repo"
    repo_path.mkdir()
    subprocess.run(["git", "init"], cwd=repo_path, check=True)
    
    # Create a skill
    skill_dir = repo_path / "skills" / "test-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("---\nname: test-skill\ndescription: A test skill\n---\n# Test Skill")
    
    # Create a rule
    rule_file = repo_path / "rules" / "test-rule.md"
    rule_file.parent.mkdir(parents=True)
    rule_file.write_text("---\nname: test-rule\ndescription: A test rule\n---\n# Test Rule")
    
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True)
    
    return repo_path

@pytest.fixture
def rune_workspace(tmp_path):
    os.chdir(tmp_path)
    from rune.main import app
    from typer.testing import CliRunner
    runner = CliRunner()
    runner.invoke(app, ["init"])
    return tmp_path
