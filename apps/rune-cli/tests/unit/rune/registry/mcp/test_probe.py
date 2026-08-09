from rune.registry.mcp.probe import PROBE_ALLOW, PROBE_ENTRY


def test_probe_entry():
    assert PROBE_ENTRY.name == "probe"
    assert PROBE_ENTRY.package == "@probelabs/probe"
    assert "roo" in PROBE_ENTRY.agent_configs
    assert PROBE_ENTRY.default_config is not None
    assert PROBE_ENTRY.default_config.alwaysAllow == PROBE_ALLOW
