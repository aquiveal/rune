from pathlib import Path
from unittest.mock import patch

from rune.repositories.config_repository import (
    add_agent_name,
    set_agent_name,
    set_remote_url,
)


def test_add_agent_name(tmp_path: Path):
    with patch("rune.repositories.git_repository.add_config") as mock_add:
        add_agent_name(tmp_path, ".roo")
        mock_add.assert_called_once_with(
            "agent.name", ".roo", tmp_path / ".rune" / "config"
        )


def test_set_agent_name(tmp_path: Path):
    with patch("rune.repositories.git_repository.set_config") as mock_set:
        set_agent_name(tmp_path, ".roo")
        mock_set.assert_called_once_with(
            "agent.name", ".roo", tmp_path / ".rune" / "config"
        )


def test_set_remote_url(tmp_path: Path):
    with patch("rune.repositories.git_repository.set_config") as mock_set:
        set_remote_url(tmp_path, "origin", "https://github.com/foo/bar.git")
        mock_set.assert_called_once_with(
            "remote.origin.url",
            "https://github.com/foo/bar.git",
            tmp_path / ".rune" / "config",
        )
