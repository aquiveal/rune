import pytest
from unittest.mock import patch
from typer.testing import CliRunner

from rune.main import app

runner = CliRunner()


@pytest.fixture
def mock_git_root(tmp_path):
    return tmp_path / "test_repo"


def test_modules_help():
    """Test that `rune modules --help` works and shows expected description."""
    result = runner.invoke(app, ["modules", "--help"])
    assert result.exit_code == 0
    assert "Manage modules contextually" in result.stdout


@patch("rune.commands.modules.Path.cwd")
@patch("rune.repositories.git_repository.get_git_root")
@patch("rune.commands.skills.scaffold_skill")
@patch("rune.services.module_service.add_module")
@patch("rune.services.skill_service.update_skill_tree")
def test_modules_add_inside_skills_root(
    mock_update_skill_tree,
    mock_add_module,
    mock_scaffold,
    mock_get_git_root,
    mock_cwd,
    mock_git_root,
):
    """Test adding a module when inside a 'skills' directory."""
    # Arrange
    skills_dir = mock_git_root / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    mock_scaffold.side_effect = lambda name, cwd: (cwd / name).mkdir(
        parents=True, exist_ok=True
    )
    mock_cwd.return_value = skills_dir
    mock_get_git_root.return_value = mock_git_root

    # Act
    result = runner.invoke(
        app, ["modules", "add", "https://github.com/user/repo", "my-skill"]
    )

    # Assert
    if result.exit_code != 0:
        print(f"Exception: {result.exception}")
        print(f"Output: {result.output}")
    assert result.exit_code == 0
    assert "Adding module" in result.output
    assert "Successfully added module" in result.output

    mock_scaffold.assert_called_once_with("my-skill", skills_dir)
    mock_add_module.assert_called_once()
    mock_update_skill_tree.assert_called_once_with(skills_dir / "my-skill")


@patch("rune.commands.modules.Path.cwd")
@patch("rune.repositories.git_repository.get_git_root")
@patch("rune.services.module_service.add_module")
@patch("rune.services.skill_service.update_skill_tree")
def test_modules_add_inside_specific_skill(
    mock_update_skill_tree,
    mock_add_module,
    mock_get_git_root,
    mock_cwd,
    mock_git_root,
):
    """Test adding a module when already inside a specific skill directory."""
    # Arrange
    my_skill_dir = mock_git_root / "skills" / "my-skill"
    my_skill_dir.mkdir(parents=True, exist_ok=True)
    mock_cwd.return_value = my_skill_dir
    mock_get_git_root.return_value = mock_git_root

    # Act
    result = runner.invoke(app, ["modules", "add", "https://github.com/user/repo"])

    # Assert
    assert result.exit_code == 0
    assert "Adding module" in result.output
    assert "Successfully added module" in result.output

    mock_add_module.assert_called_once()
    mock_update_skill_tree.assert_called_once_with(my_skill_dir)


@patch("rune.commands.modules.Path.cwd")
@patch("rune.repositories.git_repository.get_git_root")
def test_modules_add_outside_skills_context(
    mock_get_git_root,
    mock_cwd,
    mock_git_root,
):
    """Test that executing `rune modules add` outside a skills context fails with exit code 1."""
    # Arrange
    wrong_dir = mock_git_root / "other_folder"
    mock_cwd.return_value = wrong_dir
    mock_get_git_root.return_value = mock_git_root

    # Act
    result = runner.invoke(app, ["modules", "add", "https://github.com/user/repo"])

    # Assert
    assert result.exit_code == 1
    assert (
        "You must be inside a 'skills' directory to use this command" in result.output
    )


@patch("rune.commands.modules.Path.cwd")
@patch("rune.repositories.git_repository.get_git_root")
@patch("rune.commands.skills.scaffold_skill")
@patch("rune.services.module_service.add_module")
def test_modules_add_handles_fetch_failure(
    mock_add_module,
    mock_scaffold,
    mock_get_git_root,
    mock_cwd,
    mock_git_root,
):
    """Test error handling when `module_service.add_module` raises an Exception."""
    # Arrange
    skills_dir = mock_git_root / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    mock_scaffold.side_effect = lambda name, cwd: (cwd / name).mkdir(
        parents=True, exist_ok=True
    )
    mock_cwd.return_value = skills_dir
    mock_get_git_root.return_value = mock_git_root

    mock_add_module.side_effect = Exception("Mocked fetch error")

    # Act
    result = runner.invoke(
        app, ["modules", "add", "https://github.com/user/repo", "my-skill"]
    )

    # Assert
    assert result.exit_code == 1
    assert "Failed to add module" in result.output
    assert "Mocked fetch error" in result.output
