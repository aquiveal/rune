from unittest.mock import patch, MagicMock
from pathlib import Path
from rune.services.workspace_service import resolve_target_agents


def test_resolve_target_agents_with_agents_arg():
    git_root = Path("/tmp/repo")
    cwd = git_root
    agents_arg = [".roo", ".agents"]

    result = resolve_target_agents(git_root, cwd, False, agents_arg)
    assert result == [".roo", ".agents"]


@patch("rune.services.workspace_service.detect_agents")
@patch("rune.services.workspace_service.questionary")
@patch("rune.services.workspace_service.config_repository")
def test_resolve_target_agents_interactive_selection(
    mock_config, mock_questionary, mock_detect
):
    git_root = Path("/tmp/repo")
    cwd = git_root

    mock_detect.return_value = []

    mock_ask = MagicMock()
    mock_ask.ask.return_value = [".roo"]
    mock_questionary.checkbox.return_value = mock_ask

    result = resolve_target_agents(git_root, cwd, False, None)

    assert result == [".roo", ".agents"]
    mock_config.add_agent_name.assert_called_once_with(git_root, ".roo")


@patch("rune.services.workspace_service.detect_agents")
@patch("rune.services.workspace_service.questionary")
def test_resolve_target_agents_interactive_abort(mock_questionary, mock_detect):
    git_root = Path("/tmp/repo")
    cwd = git_root

    mock_detect.return_value = []

    mock_ask = MagicMock()
    mock_ask.ask.return_value = None
    mock_questionary.checkbox.return_value = mock_ask

    result = resolve_target_agents(git_root, cwd, False, None)

    assert result is None


@patch("rune.services.workspace_service.detect_agents")
@patch("rune.services.workspace_service.questionary")
def test_resolve_target_agents_interactive_empty(mock_questionary, mock_detect):
    git_root = Path("/tmp/repo")
    cwd = git_root

    mock_detect.return_value = []

    mock_ask = MagicMock()
    mock_ask.ask.return_value = []
    mock_questionary.checkbox.return_value = mock_ask

    result = resolve_target_agents(git_root, cwd, False, None)

    assert result == [".agents"]
