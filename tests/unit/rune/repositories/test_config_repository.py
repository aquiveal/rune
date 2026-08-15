from pathlib import Path
from unittest.mock import patch

from rune.repositories.config_repository import (
    add_agent_name,
    add_submodule_path,
    set_agent_name,
    set_remote_url,
    set_submodule_path,
)


def test_add_agent_name(tmp_path: Path):
    with (
        patch(
            "rune.repositories.git_repository.get_config_all", return_value=[]
        ) as mock_get,
        patch("rune.repositories.git_repository.add_config") as mock_add,
    ):
        add_agent_name(tmp_path, ".roo")
        mock_get.assert_called_once_with("agent.name", tmp_path / ".rune" / "config")
        mock_add.assert_called_once_with(
            "agent.name", ".roo", tmp_path / ".rune" / "config"
        )


def test_add_agent_name_deduplication(tmp_path: Path):
    with (
        patch(
            "rune.repositories.git_repository.get_config_all", return_value=[".roo"]
        ) as mock_get,
        patch("rune.repositories.git_repository.add_config") as mock_add,
    ):
        add_agent_name(tmp_path, ".roo")
        mock_get.assert_called_once_with("agent.name", tmp_path / ".rune" / "config")
        mock_add.assert_not_called()


def test_set_agent_name(tmp_path: Path):
    with (
        patch(
            "rune.repositories.git_repository.get_config_all", return_value=[]
        ) as mock_get,
        patch("rune.repositories.git_repository.add_config") as mock_add,
    ):
        set_agent_name(tmp_path, ".roo")
        mock_get.assert_called_once_with("agent.name", tmp_path / ".rune" / "config")
        mock_add.assert_called_once_with(
            "agent.name", ".roo", tmp_path / ".rune" / "config"
        )


def test_add_submodule_path(tmp_path: Path):
    with (
        patch(
            "rune.repositories.git_repository.get_config_all", return_value=[]
        ) as mock_get,
        patch("rune.repositories.git_repository.add_config") as mock_add,
    ):
        add_submodule_path(tmp_path, "submodules/frontend")
        mock_get.assert_called_once_with(
            "submodule.path", tmp_path / ".rune" / "config"
        )
        mock_add.assert_called_once_with(
            "submodule.path", "submodules/frontend", tmp_path / ".rune" / "config"
        )


def test_add_submodule_path_deduplication(tmp_path: Path):
    with (
        patch(
            "rune.repositories.git_repository.get_config_all",
            return_value=["submodules/frontend"],
        ) as mock_get,
        patch("rune.repositories.git_repository.add_config") as mock_add,
    ):
        add_submodule_path(tmp_path, "submodules/frontend")
        mock_get.assert_called_once_with(
            "submodule.path", tmp_path / ".rune" / "config"
        )
        mock_add.assert_not_called()


def test_set_submodule_path(tmp_path: Path):
    with (
        patch(
            "rune.repositories.git_repository.get_config_all", return_value=[]
        ) as mock_get,
        patch("rune.repositories.git_repository.add_config") as mock_add,
    ):
        set_submodule_path(tmp_path, "submodules/frontend")
        mock_get.assert_called_once_with(
            "submodule.path", tmp_path / ".rune" / "config"
        )
        mock_add.assert_called_once_with(
            "submodule.path", "submodules/frontend", tmp_path / ".rune" / "config"
        )


def test_set_remote_url(tmp_path: Path):
    with patch("rune.repositories.git_repository.set_config") as mock_set:
        set_remote_url(tmp_path, "origin", "https://github.com/foo/bar.git")
        mock_set.assert_called_once_with(
            "remote.origin.url",
            "https://github.com/foo/bar.git",
            tmp_path / ".rune" / "config",
        )
