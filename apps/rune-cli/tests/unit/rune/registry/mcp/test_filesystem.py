from rune.registry.mcp.filesystem import FILESYSTEM_ENTRY


def test_filesystem_entry():
    assert FILESYSTEM_ENTRY.name == "filesystem"
    assert FILESYSTEM_ENTRY.package == "@modelcontextprotocol/server-filesystem"
    assert FILESYSTEM_ENTRY.default_config is not None
    assert "${workspaceFolder}" in FILESYSTEM_ENTRY.default_config.args
