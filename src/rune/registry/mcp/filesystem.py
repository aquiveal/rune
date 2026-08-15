from rune.schemas.mcp_schema import McpRegistryEntry, McpStdioServer

__all__ = ["FILESYSTEM_ENTRY"]

FILESYSTEM_ENTRY = McpRegistryEntry(
    name="filesystem",
    description="File system access MCP server for reading and modifying local files.",
    repository="https://github.com/modelcontextprotocol/servers.git",
    package="@modelcontextprotocol/server-filesystem",
    default_config=McpStdioServer(
        type="stdio",
        command="npx",
        args=[
            "-y",
            "@modelcontextprotocol/server-filesystem",
            "${workspaceFolder}",
        ],
    ),
)
