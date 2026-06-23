from pathlib import Path
from rune.utils.url import parse_github_url, resolve_url


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
