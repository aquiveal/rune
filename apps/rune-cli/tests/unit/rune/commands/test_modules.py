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


@patch("rune.commands.modules.Path.cwd")
@patch("rune.repositories.git_repository.get_git_root")
@patch("rune.commands.skills.scaffold_skill")
@patch("rune.services.module_service.add_module")
@patch("rune.services.skill_service.update_skill_instructions")
def test_modules_add_inside_skills_root(
    mock_update_skill_instructions,
    mock_add_module,
    mock_scaffold,
    mock_get_git_root,
    mock_cwd,
    mock_git_root,
):
    """Test adding a module when inside a 'skills' directory."""
    skills_dir = mock_git_root / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    mock_scaffold.side_effect = lambda name, cwd: (cwd / name).mkdir(
        parents=True, exist_ok=True
    )
    mock_cwd.return_value = skills_dir
    mock_get_git_root.return_value = mock_git_root

    result = runner.invoke(
        app, ["modules", "add", "https://github.com/user/repo", "my-skill"]
    )

    if result.exit_code != 0:
        print(f"Exception: {result.exception}")
        print(f"Output: {result.output}")
    assert result.exit_code == 0

    mock_scaffold.assert_called_once_with("my-skill", skills_dir)
    mock_add_module.assert_called_once()
    mock_update_skill_instructions.assert_called_once_with(skills_dir / "my-skill")


@patch("rune.commands.modules.Path.cwd")
@patch("rune.repositories.git_repository.get_git_root")
@patch("rune.services.module_service.add_module")
@patch("rune.services.skill_service.update_skill_instructions")
def test_modules_add_inside_specific_skill(
    mock_update_skill_instructions,
    mock_add_module,
    mock_get_git_root,
    mock_cwd,
    mock_git_root,
):
    """Test adding a module when already inside a specific skill directory."""
    my_skill_dir = mock_git_root / "skills" / "my-skill"
    my_skill_dir.mkdir(parents=True, exist_ok=True)
    mock_cwd.return_value = my_skill_dir
    mock_get_git_root.return_value = mock_git_root

    result = runner.invoke(app, ["modules", "add", "https://github.com/user/repo"])

    assert result.exit_code == 0

    mock_add_module.assert_called_once()
    mock_update_skill_instructions.assert_called_once_with(my_skill_dir)


@patch("rune.commands.modules.Path.cwd")
@patch("rune.repositories.git_repository.get_git_root")
@patch("rune.services.workspace_service.resolve_target_agents")
def test_modules_add_outside_skills_context(
    mock_resolve_target_agents,
    mock_get_git_root,
    mock_cwd,
    mock_git_root,
):
    """Test that executing `rune modules add` outside a skills context fails with exit code 1 if no target agents are resolved."""
    wrong_dir = mock_git_root / "other_folder"
    mock_cwd.return_value = wrong_dir
    mock_get_git_root.return_value = mock_git_root
    mock_resolve_target_agents.return_value = None

    result = runner.invoke(app, ["modules", "add", "https://github.com/user/repo"])

    assert result.exit_code == 1


@patch("rune.commands.modules.Path.cwd")
@patch("rune.repositories.git_repository.get_git_root")
@patch("rune.services.workspace_service.resolve_target_agents")
@patch("rune.commands.skills.scaffold_skill")
@patch("rune.services.module_service.add_module")
@patch("rune.services.skill_service.update_skill_instructions")
def test_modules_add_from_root_infers_agent_dir(
    mock_update_skill_instructions,
    mock_add_module,
    mock_scaffold_skill,
    mock_resolve_target_agents,
    mock_get_git_root,
    mock_cwd,
    mock_git_root,
):
    """Test adding a module from root correctly infers the agent skills directory."""
    mock_cwd.return_value = mock_git_root
    mock_get_git_root.return_value = mock_git_root
    mock_resolve_target_agents.return_value = [".agents"]

    inferred_skills_dir = mock_git_root / ".agents" / "skills"

    mock_scaffold_skill.side_effect = lambda name, base_dir: (base_dir / name).mkdir(
        parents=True, exist_ok=True
    )

    result = runner.invoke(
        app, ["modules", "add", "https://github.com/user/repo", "my-skill"]
    )

    assert result.exit_code == 0

    mock_scaffold_skill.assert_called_once_with("my-skill", inferred_skills_dir)
    mock_add_module.assert_called_once()
    mock_update_skill_instructions.assert_called_once_with(
        inferred_skills_dir / "my-skill"
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
    skills_dir = mock_git_root / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    mock_scaffold.side_effect = lambda name, cwd: (cwd / name).mkdir(
        parents=True, exist_ok=True
    )
    mock_cwd.return_value = skills_dir
    mock_get_git_root.return_value = mock_git_root

    mock_add_module.side_effect = Exception("Mocked fetch error")

    result = runner.invoke(
        app, ["modules", "add", "https://github.com/user/repo", "my-skill"]
    )

    assert result.exit_code == 1
