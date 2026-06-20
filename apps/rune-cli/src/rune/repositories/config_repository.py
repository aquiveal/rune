from pathlib import Path
from typing import List, Optional
from rune.repositories import git_repository
from rune.config.main import RUNE_DIR, RUNE_CONFIG

def _get_config_path(root_dir: Path) -> Path:
    return root_dir / RUNE_DIR / RUNE_CONFIG

def get_agent_names(root_dir: Path) -> List[str]:
    return git_repository.get_config_all("agent.name", _get_config_path(root_dir))

def add_agent_name(root_dir: Path, name: str):
    git_repository.add_config("agent.name", name, _get_config_path(root_dir))

def set_agent_name(root_dir: Path, name: str):
    git_repository.set_config("agent.name", name, _get_config_path(root_dir))

def get_remote_url(root_dir: Path, alias: str) -> Optional[str]:
    return git_repository.get_config(f"remote.{alias}.url", _get_config_path(root_dir))

def set_remote_url(root_dir: Path, alias: str, url: str):
    git_repository.set_config(f"remote.{alias}.url", url, _get_config_path(root_dir))

def get_repomap_model(root_dir: Path) -> str:
    return git_repository.get_config("repomap.model", _get_config_path(root_dir)) or "gemini/gemini-3.1-flash-lite"
