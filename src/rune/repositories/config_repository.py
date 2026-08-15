# src/rune/repositories/config_repository.py
from pathlib import Path

from rune.repositories import git_repository

__all__ = [
    "add_agent_name",
    "add_submodule_path",
    "get_agent_names",
    "get_submodule_paths",
    "set_agent_name",
    "set_remote_url",
    "set_submodule_path",
]


def _get_config_path(root_dir: Path) -> Path:
    return root_dir / ".rune" / "config"


def get_agent_names(root_dir: Path) -> list[str]:
    return git_repository.get_config_all("agent.name", _get_config_path(root_dir))


def add_agent_name(root_dir: Path, name: str):
    existing = get_agent_names(root_dir)
    if name not in existing:
        git_repository.add_config("agent.name", name, _get_config_path(root_dir))


def set_agent_name(root_dir: Path, name: str):
    add_agent_name(root_dir, name)


def set_remote_url(root_dir: Path, alias: str, url: str):
    git_repository.set_config(f"remote.{alias}.url", url, _get_config_path(root_dir))


def get_submodule_paths(root_dir: Path) -> list[str]:
    return git_repository.get_config_all("submodule.path", _get_config_path(root_dir))


def add_submodule_path(root_dir: Path, path: str):
    existing = get_submodule_paths(root_dir)
    if path not in existing:
        git_repository.add_config("submodule.path", path, _get_config_path(root_dir))


def set_submodule_path(root_dir: Path, path: str):
    add_submodule_path(root_dir, path)
