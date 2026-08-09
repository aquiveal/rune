from rune.registry.mcp.memory import MEMORY_ENTRY


def test_memory_entry():
    assert MEMORY_ENTRY.name == "memory"
    assert MEMORY_ENTRY.package == "@modelcontextprotocol/server-memory"
    assert MEMORY_ENTRY.default_config is not None
