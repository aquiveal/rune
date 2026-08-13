from pathlib import Path

from rune.utils.url import (
    is_git_source,
    is_web_url,
    parse_github_url,
    resolve_relative_url,
    resolve_url,
    slugify_url,
)


def test_parse_github_url_standard():
    url = "https://github.com/aquiveal/rune"
    base_url, path = parse_github_url(url)
    assert base_url == "https://github.com/aquiveal/rune.git"
    assert path is None


def test_parse_github_url_tree():
    url = "https://github.com/aquiveal/rune/tree/main/apps/rune-cli"
    base_url, path = parse_github_url(url)
    assert base_url == "https://github.com/aquiveal/rune.git"
    assert path == "apps/rune-cli"


def test_parse_github_url_blob():
    url = "https://github.com/aquiveal/rune/blob/master/README.md"
    base_url, path = parse_github_url(url)
    assert base_url == "https://github.com/aquiveal/rune.git"
    assert path == "README.md"


def test_parse_github_url_nested_branch():
    url = "https://github.com/aquiveal/rune/tree/feat/my-branch/apps/rune-cli"
    base_url, path = parse_github_url(url)
    assert base_url == "https://github.com/aquiveal/rune.git"
    assert path == "my-branch/apps/rune-cli"


def test_resolve_url_local(tmp_path):
    (tmp_path / "testdir").mkdir()
    resolved = resolve_url(str(tmp_path / "testdir"), tmp_path)
    assert resolved == str((tmp_path / "testdir").absolute())


def test_resolve_url_owner_repo():
    resolved = resolve_url("aquiveal/rune", Path("/tmp"))
    assert resolved == "https://github.com/aquiveal/rune.git"


def test_resolve_url_already_valid():
    resolved = resolve_url("https://github.com/aquiveal/rune.git", Path("/tmp"))
    assert resolved == "https://github.com/aquiveal/rune.git"


def test_is_web_url():
    assert is_web_url("https://developer-docs.amazon/sp-api/reference") is True
    assert is_web_url("http://example.com/docs") is True
    assert is_web_url("https://github.com/aquiveal/rune.git") is False
    assert is_web_url("git@github.com:aquiveal/rune.git") is False
    assert is_web_url("owner/repo") is False


def test_is_git_source():
    assert is_git_source("https://github.com/aquiveal/rune.git") is True
    assert is_git_source("git@github.com:aquiveal/rune.git") is True
    assert is_git_source("file:///tmp/repo.git") is True
    assert is_git_source("aquiveal/rune") is True
    assert is_git_source("https://developer-docs.amazon/sp-api") is False


def test_slugify_url():
    slug = slugify_url("https://developer-docs.amazon/sp-api/reference/welcome-to-api-references")
    assert slug == "reference-welcome-to-api-references"

    slug_root = slugify_url("https://docs.anthropic.com")
    assert slug_root == "anthropic"


def test_resolve_relative_url():
    base = "https://example.com/sp-api/reference/welcome"
    rel = "orders-api-v0-reference#section-1"
    resolved = resolve_relative_url(base, rel)
    assert resolved == "https://example.com/sp-api/reference/orders-api-v0-reference"

