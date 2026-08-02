from pathlib import Path

from rune.schemas.mcp_schema import McpStdioServer
from rune.services import mcp_service


def test_builtin_registry():
    registry = mcp_service.get_builtin_registry()
    assert "probe" in registry
    assert "probelabs/probe" in registry
    probe_entry = registry["probe"]
    assert probe_entry.name == "probe"
    assert "roo" in probe_entry.agent_configs


def test_search_registry():
    results = mcp_service.search_registry("probe")
    assert len(results) >= 1
    assert any(r.name == "probe" for r in results)


def test_add_mcp_server_from_registry(tmp_path: Path):
    git_root = tmp_path
    (git_root / ".roo").mkdir()
    updated = mcp_service.add_mcp_server(
        source="probelabs/probe",
        git_root=git_root,
        cwd=git_root,
        global_scope=False,
    )
    assert len(updated) > 0
    # Check .roo/mcp.json
    roo_json = git_root / ".roo" / "mcp.json"
    assert roo_json.exists()
    content = roo_json.read_text(encoding="utf-8")
    assert "probe" in content


def test_add_custom_stdio_server(tmp_path: Path):
    git_root = tmp_path
    (git_root / ".roo").mkdir()
    custom = McpStdioServer(
        type="stdio",
        command="python",
        args=["-m", "custom_mcp"],
    )
    updated = mcp_service.add_mcp_server(
        source="my-custom-mcp",
        git_root=git_root,
        cwd=git_root,
        global_scope=False,
        custom_config=custom,
    )
    assert len(updated) > 0
    roo_json = git_root / ".roo" / "mcp.json"
    assert roo_json.exists()
    content = roo_json.read_text(encoding="utf-8")
    assert "my-custom-mcp" in content
    assert "custom_mcp" in content


def test_list_and_remove_mcp_servers(tmp_path: Path):
    git_root = tmp_path
    (git_root / ".roo").mkdir()
    mcp_service.add_mcp_server(
        source="probe",
        git_root=git_root,
        cwd=git_root,
        global_scope=False,
    )
    servers = mcp_service.list_mcp_servers(git_root, global_scope=False)
    assert "probe" in servers

    removed = mcp_service.remove_mcp_server(["probe"], git_root, global_scope=False)
    assert len(removed) > 0

    servers_after = mcp_service.list_mcp_servers(git_root, global_scope=False)
    assert "probe" not in servers_after
