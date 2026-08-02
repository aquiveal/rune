from unittest.mock import patch
from pathlib import Path
from rune.services.workspace_service import resolve_target_agents


def test_resolve_target_agents_with_agents_arg():
    git_root = Path("/tmp/repo")
    cwd = git_root
    agents_arg = [".roo", ".agents"]

    result = resolve_target_agents(git_root, cwd, False, agents_arg)
    assert result == [".roo", ".agents"]


@patch("rune.services.workspace_service.detect_agents")
@patch("rune.services.workspace_service.config_repository")
def test_resolve_target_agents_defaults_to_agents(mock_config, mock_detect):
    git_root = Path("/tmp/repo")
    cwd = git_root

    mock_detect.return_value = []

    result = resolve_target_agents(git_root, cwd, False, None)

    assert result == [".agents"]
    mock_config.add_agent_name.assert_called_once_with(git_root, ".agents")
