import re
import urllib.parse
from pathlib import Path

from rune.config.main import settings

__all__ = [
    "is_git_source",
    "is_web_url",
    "parse_github_url",
    "resolve_relative_url",
    "resolve_url",
    "slugify_url",
]


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


def is_web_url(source: str) -> bool:
    """Check if the source is an HTTP/HTTPS web or documentation URL."""
    if not source.startswith(("http://", "https://")):
        return False
    if source.endswith(".git"):
        return False
    return True


def is_git_source(source: str) -> bool:
    """Check if the source is explicitly a Git repository URL or remote."""
    if source.endswith(".git") or source.startswith(("git@", "file://")):
        return True
    return bool(
        "/" in source
        and not source.startswith(("http://", "https://"))
        and not Path(source).exists()
    )


def slugify_url(url: str) -> str:
    """Generate a clean rule name slug from a web or documentation URL."""
    parsed = urllib.parse.urlparse(url)
    path = parsed.path.strip("/")

    if path:
        # Extract meaningful path segments (up to the last 2 segments)
        segments = [s for s in path.split("/") if s]
        slug_raw = "-".join(segments[-2:]) if len(segments) >= 2 else segments[0]
    else:
        # Fallback to domain name
        domain = parsed.netloc.split(":")[0]
        for prefix in ["docs.", "developer.", "developer-docs.", "api.", "www."]:
            if domain.startswith(prefix):
                domain = domain[len(prefix) :]
                break
        slug_raw = domain.split(".")[0]

    # Clean non-alphanumeric chars
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", slug_raw).strip("-").lower()
    return slug or "documentation-rule"


def resolve_relative_url(base_url: str, relative_url: str) -> str:
    """Resolve a relative URL against a base URL and strip fragment identifiers."""
    joined = urllib.parse.urljoin(base_url, relative_url)
    parsed = urllib.parse.urlparse(joined)
    # Strip URL fragment (#section)
    clean_url = urllib.parse.urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            "",
        )
    )
    return clean_url


