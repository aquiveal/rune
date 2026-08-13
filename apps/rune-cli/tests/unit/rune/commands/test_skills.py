import os
import subprocess

from rune.main import app
from typer.testing import CliRunner

runner = CliRunner()


def test_skills_add_shorthand(tmp_path, mock_git_repo):
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)
    runner.invoke(app, ["config", "--add", "agent.name", ".roo"])

    repo_url = "file:///" + str(mock_git_repo).replace("\\", "/")
    # We use the full URL here because shorthand resolution for local paths isn't implemented yet
    result = runner.invoke(app, ["skills", "add", repo_url, "--agent", ".roo"])

    if result.exit_code != 0:
        print(result.output)
        if result.exception:
            print(result.exception)

    assert result.exit_code == 0

    assert (tmp_path / ".roo" / "skills" / "test-skill" / "SKILL.md").exists()


def test_skills_list(tmp_path, mock_git_repo):
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)
    repo_url = "file:///" + str(mock_git_repo).replace("\\", "/")
    runner.invoke(app, ["skills", "add", repo_url, "--agent", ".roo"])

    result = runner.invoke(app, ["skills", "list"])
    assert result.exit_code == 0


def test_skills_validate(tmp_path):
    os.chdir(tmp_path)
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: test-skill\ndescription: valid\n---\n"
    )

    result = runner.invoke(app, ["skills", "validate", str(skill_dir)])
    assert result.exit_code == 0

    # Invalid name
    (skill_dir / "SKILL.md").write_text("---\nname: Invalid\ndescription: valid\n---\n")
    result = runner.invoke(app, ["skills", "validate", str(skill_dir)])
    assert result.exit_code == 1


def test_skills_init(tmp_path):
    os.chdir(tmp_path)
    result = runner.invoke(app, ["skills", "init", "my-skill"])
    assert result.exit_code == 0
    assert (tmp_path / "my-skill" / "modules").exists()
    assert (tmp_path / "my-skill" / "scripts").exists()
    assert (tmp_path / "my-skill" / "SKILL.md").exists()


def test_skills_update(tmp_path):
    os.chdir(tmp_path)
    # Create a skill
    runner.invoke(app, ["skills", "init", "my-skill"])

    # Run update inside the skill
    os.chdir(tmp_path / "my-skill")
    subprocess.run(["git", "init"], check=True)
    result = runner.invoke(app, ["skills", "update"])
    assert result.exit_code == 0

    skill_md = (tmp_path / "my-skill" / "SKILL.md").read_text()
    assert "name: my-skill" in skill_md
    assert "## File Tree" in skill_md
    assert (tmp_path / "my-skill" / "modules").is_dir()
