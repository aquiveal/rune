from pathlib import Path

import structlog
import yaml

from rune.config.exceptions import RuneError

__all__ = ["parse_gitignore", "update_mutagen_ignore"]

logger = structlog.get_logger(__name__)


def parse_gitignore(gitignore_path: Path) -> list[str]:
    """Parse ignore patterns from a .gitignore file, excluding comments and blank lines."""
    if not gitignore_path.exists():
        raise RuneError(f".gitignore file not found at '{gitignore_path}'")

    content = gitignore_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    patterns: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped not in patterns:
            patterns.append(stripped)

    return patterns


def update_mutagen_ignore(
    git_root: Path,
    gitignore_path: Path | None = None,
    mutagen_path: Path | None = None,
) -> tuple[Path, int]:
    """Copy .gitignore ignore patterns into mutagen.yml defaults ignore list.

    Always touches strictly sync.defaults.ignore.paths and leaves other keys untouched.
    """
    target_gitignore = gitignore_path or (git_root / ".gitignore")
    target_mutagen = mutagen_path or (git_root / "mutagen.yml")

    patterns = parse_gitignore(target_gitignore)

    if not target_mutagen.exists():
        raise RuneError(f"mutagen.yml file not found at '{target_mutagen}'")

    try:
        content = target_mutagen.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        if not isinstance(data, dict):
            data = {}
    except Exception as e:
        raise RuneError(f"Failed to parse mutagen.yml at '{target_mutagen}': {e}") from e

    # Ensure sync.defaults.ignore.paths structure exists
    sync_data = data.setdefault("sync", {})
    if not isinstance(sync_data, dict):
        sync_data = {}
        data["sync"] = sync_data

    defaults_data = sync_data.setdefault("defaults", {})
    if not isinstance(defaults_data, dict):
        defaults_data = {}
        sync_data["defaults"] = defaults_data

    ignore_data = defaults_data.setdefault("ignore", {})
    if not isinstance(ignore_data, dict):
        ignore_data = {}
        defaults_data["ignore"] = ignore_data

    existing_paths = ignore_data.setdefault("paths", [])
    if not isinstance(existing_paths, list):
        existing_paths = []
        ignore_data["paths"] = existing_paths

    added_count = 0
    for pattern in patterns:
        if pattern not in existing_paths:
            existing_paths.append(pattern)
            added_count += 1

    try:
        updated_content = yaml.dump(data, sort_keys=False, default_flow_style=False)
        target_mutagen.write_text(updated_content, encoding="utf-8")
    except Exception as e:
        raise RuneError(f"Failed to write mutagen.yml at '{target_mutagen}': {e}") from e

    return target_mutagen, added_count
