import pytest
from pydantic import ValidationError

from rune.schemas.mcp_schema import (
    McpRegistryEntry,
    McpSettings,
    McpSseServer,
    McpStdioServer,
    McpStreamableHttpServer,
)


def test_stdio_server_valid():
    server = McpStdioServer(
        type="stdio",
        command="node",
        args=["server.js"],
        env={"API_KEY": "secret"},
    )
    assert server.type == "stdio"
    assert server.command == "node"
    assert server.args == ["server.js"]
    assert server.env == {"API_KEY": "secret"}


def test_stdio_server_rejects_url():
    with pytest.raises(ValidationError):
        McpStdioServer.model_validate(
            {
                "type": "stdio",
                "command": "node",
                "url": "http://localhost:8080",
            }
        )


def test_sse_server_valid():
    server = McpSseServer(
        type="sse",
        url="https://mcp.example.com/sse",
        headers={"Authorization": "Bearer token"},
    )
    assert server.type == "sse"
    assert server.url == "https://mcp.example.com/sse"
    assert server.headers == {"Authorization": "Bearer token"}


def test_sse_server_rejects_command():
    with pytest.raises(ValidationError):
        McpSseServer.model_validate(
            {
                "type": "sse",
                "url": "https://mcp.example.com/sse",
                "command": "node",
            }
        )


def test_streamable_http_server_valid():
    server = McpStreamableHttpServer(
        type="streamable-http",
        url="https://mcp.example.com/mcp",
    )
    assert server.type == "streamable-http"
    assert server.url == "https://mcp.example.com/mcp"


def test_streamable_http_server_rejects_args():
    with pytest.raises(ValidationError):
        McpStreamableHttpServer.model_validate(
            {
                "type": "streamable-http",
                "url": "https://mcp.example.com/mcp",
                "args": ["--verbose"],
            }
        )


def test_mcp_settings_parsing():
    data = {
        "mcpServers": {
            "probe": {
                "type": "stdio",
                "command": "npx",
                "args": ["-y", "@probelabs/probe@latest", "agent", "--mcp"],
            },
            "remote-sse": {
                "type": "sse",
                "url": "https://mcp.example.com/sse",
            },
        }
    }
    settings = McpSettings.model_validate(data)
    assert len(settings.mcpServers) == 2
    assert isinstance(settings.mcpServers["probe"], McpStdioServer)
    assert isinstance(settings.mcpServers["remote-sse"], McpSseServer)


def test_mcp_registry_entry():
    entry = McpRegistryEntry(
        name="probe",
        description="Probe context engine",
        agent_configs={
            "roo": McpStdioServer(type="stdio", command="npx", args=["probe", "agent"]),
            "cursor": McpStdioServer(
                type="stdio", command="npx", args=["probe", "mcp"]
            ),
        },
    )
    assert entry.name == "probe"
    assert "roo" in entry.agent_configs
    assert entry.agent_configs["roo"].args == ["probe", "agent"]
