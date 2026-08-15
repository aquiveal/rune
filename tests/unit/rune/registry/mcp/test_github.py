from rune.registry.mcp.github import GITHUB_ENTRY


def test_github_entry():
    assert GITHUB_ENTRY.name == "github"
    assert GITHUB_ENTRY.package == "@modelcontextprotocol/server-github"
    assert GITHUB_ENTRY.default_config is not None
    assert "GITHUB_PERSONAL_ACCESS_TOKEN" in GITHUB_ENTRY.default_config.env
