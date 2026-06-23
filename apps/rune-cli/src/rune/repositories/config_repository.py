from pathlib import Path
from rune.repositories import git_repository


def _get_config_path(root_dir: Path) -> Path:
    return root_dir / ".rune" / "config"


def add_agent_name(root_dir: Path, name: str):
    git_repository.add_config("agent.name", name, _get_config_path(root_dir))


def set_agent_name(root_dir: Path, name: str):
    git_repository.set_config("agent.name", name, _get_config_path(root_dir))


def set_remote_url(root_dir: Path, alias: str, url: str):
    git_repository.set_config(f"remote.{alias}.url", url, _get_config_path(root_dir))
