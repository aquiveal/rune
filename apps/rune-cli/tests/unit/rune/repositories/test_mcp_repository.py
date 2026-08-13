from pathlib import Path

import pytest
from rune.config.exceptions import ConfigError
from rune.repositories import mcp_repository
from rune.schemas.mcp_schema import McpSettings, McpStdioServer


def test_get_agent_mcp_config_path_workspace(tmp_path: Path):
    roo_path = mcp_repository.get_agent_mcp_config_path(
        tmp_path, "roo", global_scope=False
    )
    assert roo_path == tmp_path / ".roo" / "mcp.json"

    claude_path = mcp_repository.get_agent_mcp_config_path(
        tmp_path, ".claude", global_scope=False
    )
    assert claude_path == tmp_path / ".claude" / "mcp.json"


def test_load_non_existent_config(tmp_path: Path):
    path = tmp_path / "mcp.json"
    settings = mcp_repository.load_mcp_config(path)
    assert isinstance(settings, McpSettings)
    assert settings.mcpServers == {}


def test_save_and_load_mcp_config(tmp_path: Path):
    path = tmp_path / ".roo" / "mcp.json"
    settings = McpSettings(
        mcpServers={
            "probe": McpStdioServer(type="stdio", command="npx", args=["probe"])
        }
    )
    mcp_repository.save_mcp_config(path, settings)

    assert path.exists()
    loaded = mcp_repository.load_mcp_config(path)
    assert "probe" in loaded.mcpServers
    assert loaded.mcpServers["probe"].command == "npx"


def test_add_and_remove_server_config(tmp_path: Path):
    path = tmp_path / "mcp.json"
    srv = McpStdioServer(type="stdio", command="node", args=["index.js"])

    mcp_repository.add_server_config(path, "my-server", srv)
    loaded = mcp_repository.load_mcp_config(path)
    assert "my-server" in loaded.mcpServers

    removed = mcp_repository.remove_server_config(path, "my-server")
    assert removed is True

    loaded_after = mcp_repository.load_mcp_config(path)
    assert "my-server" not in loaded_after.mcpServers


def test_add_server_config_preserves_always_allow_and_env(tmp_path: Path):
    path = tmp_path / "mcp.json"
    existing_srv = McpStdioServer(
        type="stdio",
        command="node",
        args=["index.js"],
        alwaysAllow=["custom_tool_1", "custom_tool_2"],
        env={"EXISTING_VAR": "FOO", "OVERRIDDEN_VAR": "OLD"},
    )
    mcp_repository.add_server_config(path, "my-server", existing_srv)

    updated_srv = McpStdioServer(
        type="stdio",
        command="node",
        args=["index.js", "--updated"],
        alwaysAllow=["new_tool_3"],
        env={"OVERRIDDEN_VAR": "NEW", "NEW_VAR": "BAR"},
    )
    mcp_repository.add_server_config(path, "my-server", updated_srv)

    loaded = mcp_repository.load_mcp_config(path)
    server = loaded.mcpServers["my-server"]
    assert server.alwaysAllow == ["custom_tool_1", "custom_tool_2", "new_tool_3"]
    assert server.env == {
        "EXISTING_VAR": "FOO",
        "OVERRIDDEN_VAR": "NEW",
        "NEW_VAR": "BAR",
    }


def test_load_corrupted_json(tmp_path: Path):
    path = tmp_path / "corrupted.json"
    path.write_text("{ invalid json }", encoding="utf-8")

    with pytest.raises(ConfigError):
        mcp_repository.load_mcp_config(path)
