"""Utils package for Rune CLI."""

from rune.utils import git, os, url
from rune.utils.git import (
    GitError,
    get_git_root,
    is_github_folder_url,
    is_github_url,
)
from rune.utils.os import (
    elevate_and_run,
    is_admin,
)
from rune.utils.url import (
    is_git,
    is_git_source,
    is_site,
    is_web_url,
    parse_github_url,
    resolve_relative_url,
    resolve_url,
    slugify_url,
)

__all__ = [
    "GitError",
    "elevate_and_run",
    "get_git_root",
    "git",
    "is_admin",
    "is_git",
    "is_git_source",
    "is_github_folder_url",
    "is_github_url",
    "is_site",
    "is_web_url",
    "os",
    "parse_github_url",
    "resolve_relative_url",
    "resolve_url",
    "slugify_url",
    "url",
]
