from rune.schemas.mcp_schema import McpRegistryEntry, McpStdioServer

__all__ = ["MEMORY_ENTRY"]

MEMORY_ENTRY = McpRegistryEntry(
    name="memory",
    description="Knowledge graph persistent memory MCP server.",
    repository="https://github.com/modelcontextprotocol/servers.git",
    package="@modelcontextprotocol/server-memory",
    default_config=McpStdioServer(
        type="stdio",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-memory"],
    ),
)
