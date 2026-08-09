from pathlib import Path

from rune.config.main import settings

__all__ = ["parse_github_url", "resolve_url"]


def resolve_url(source: str, root_dir: Path) -> str:
    """Resolve a source string into a full repository URL or absolute path."""
    if Path(source).exists():
        return str(Path(source).absolute())
    url = settings.remotes.get(source)
    if url:
        return url
    if "/" in source and not source.startswith(
        ("http://", "https://", "git@", "file://")
    ):
        return f"https://github.com/{source}.git"
    return source


def parse_github_url(url: str) -> tuple[str, str | None]:
    """Parse a GitHub URL into base repo URL and optional path."""
    if "github.com" in url:
        for delimiter in ["/tree/", "/blob/"]:
            if delimiter in url:
                parts = url.split(delimiter)
                base_url = parts[0]
                if not base_url.endswith(".git"):
                    base_url += ".git"

                # Extract path after the branch name
                path_parts = parts[1].split("/", 1)
                path = path_parts[1] if len(path_parts) > 1 else None
                return base_url, path
        if not url.endswith(".git"):
            return url + ".git", None
    return url, None
