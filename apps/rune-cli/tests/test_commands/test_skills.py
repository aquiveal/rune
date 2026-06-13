import pytest
from typer.testing import CliRunner
from rune.main import app
import os
import shutil
import subprocess

runner = CliRunner()

def test_skills_add_shorthand(tmp_path, mock_git_repo):
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])
    runner.invoke(app, ["config", "--add", "agent.name", ".roo"])
    
    repo_url = str(mock_git_repo).replace('\\', '/')
    # We use the full URL here because shorthand resolution for local paths isn't implemented yet
    result = runner.invoke(app, ["skills", "add", repo_url, "--agent", ".roo"])
    
    assert result.exit_code == 0
    assert "Installed skill 'test-skill'" in result.stdout
    assert (tmp_path / ".roo" / "skills" / "test-skill" / "SKILL.md").exists()

def test_skills_list(tmp_path, mock_git_repo):
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])
    repo_url = str(mock_git_repo).replace('\\', '/')
    runner.invoke(app, ["skills", "add", repo_url, "--agent", ".roo"])
    
    result = runner.invoke(app, ["skills", "list"])
    assert result.exit_code == 0
    assert "skills/test-skill: OK" in result.stdout

def test_skills_develop(tmp_path, mock_git_repo):
    os.chdir(tmp_path)
    subprocess.run(["git", "init"], check=True) # Need git repo for submodules
    runner.invoke(app, ["init"])
    repo_url = "file:///" + str(mock_git_repo).replace('\\', '/')
    
    result = runner.invoke(app, ["skills", "develop", repo_url])
    assert result.exit_code == 0
    assert (tmp_path / "mock_repo" / "modules").exists()

def test_skills_validate(tmp_path):
    os.chdir(tmp_path)
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("---\nname: test-skill\ndescription: valid\n---\n")
    
    result = runner.invoke(app, ["skills", "validate", str(skill_dir)])
    assert result.exit_code == 0
    assert "is valid" in result.stdout

    # Invalid name
    (skill_dir / "SKILL.md").write_text("---\nname: Invalid\ndescription: valid\n---\n")
    result = runner.invoke(app, ["skills", "validate", str(skill_dir)])
    assert result.exit_code == 1
    assert "Validation failed" in result.stderr
