import os
import subprocess
from unittest.mock import patch

from typer.testing import CliRunner

from rune.main import app

runner = CliRunner()


def test_rules_add(tmp_path, mock_git_repo):
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])

    # Initialize git repo for submodules
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)

    repo_url = "file:///" + str(mock_git_repo).replace("\\", "/")
    result = runner.invoke(app, ["rules", "add", repo_url, "--agent", ".roo"])

    if result.exit_code != 0:
        print(result.output)
        if result.exception:
            print(result.exception)

    assert result.exit_code == 0

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


def test_rule_filtering(tmp_path, mock_git_repo):
    # Verify that passing `--rule architecture-application` correctly filters the discovered list
    # and flags `architecture-application.md` for installation.
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)

    # Create architecture-application.md in mock repo (without frontmatter)
    arch_file = mock_git_repo / "rules" / "architecture-application.md"
    arch_file.write_text("# Arch App")
    subprocess.run(["git", "add", "."], cwd=mock_git_repo, check=True)
    subprocess.run(
        ["git", "commit", "-m", "Add arch rule"], cwd=mock_git_repo, check=True
    )

    repo_url = "file:///" + str(mock_git_repo).replace("\\", "/")
    result = runner.invoke(
        app,
        [
            "rules",
            "add",
            repo_url,
            "--rule",
            "architecture-application",
            "--agent",
            ".roo",
        ],
    )

    assert result.exit_code == 0


@patch("rune.services.module_service.add_module")
def test_implicit_agents_injection(mock_add_module, tmp_path, mock_git_repo):
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)

    repo_url = "file:///" + str(mock_git_repo).replace("\\", "/")
    # Without --agent, assuming defaults via questionary bypass or no prompt mock needed if we mock add_module?
    # Wait, questionary.checkbox().ask() is called. We should mock it to return [] or handle no interaction.
    with patch("questionary.checkbox") as mock_checkbox:
        mock_checkbox.return_value.ask.return_value = []  # User skips selecting additional agents
        result = runner.invoke(app, ["rules", "add", repo_url, "--rule", "test-rule"])

    assert result.exit_code == 0

    # Check that add_module was called with target_agents including ['.agents']
    assert mock_add_module.called
    kwargs = mock_add_module.call_args.kwargs
    assert ".agents" in kwargs.get("agents", [])


def test_rule_filtering_edge_cases(tmp_path, mock_git_repo):
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)

    repo_url = "file:///" + str(mock_git_repo).replace("\\", "/")

    # Test invalid rule
    result = runner.invoke(
        app,
        ["rules", "add", repo_url, "--rule", "invalid-rule-name", "--agent", ".roo"],
    )
    assert result.exit_code == 1

    # Test permutations with and without .md
    # Create another rule with frontmatter name `some-rule` but filename `some-rule.md`
    some_rule_file = mock_git_repo / "rules" / "some-rule.md"
    some_rule_file.write_text(
        "---\nname: some-rule\ndescription: some desc\n---\n# Some Rule"
    )
    subprocess.run(["git", "add", "."], cwd=mock_git_repo, check=True)
    subprocess.run(
        ["git", "commit", "-m", "Add some rule"], cwd=mock_git_repo, check=True
    )

    # Test multiple rules
    result = runner.invoke(
        app,
        [
            "rules",
            "add",
            repo_url,
            "--rule",
            "test-rule",
            "--rule",
            "some-rule",
            "--agent",
            ".roo",
        ],
    )
    assert result.exit_code == 0
