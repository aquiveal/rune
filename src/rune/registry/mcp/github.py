from rune.schemas.mcp_schema import McpRegistryEntry, McpStdioServer

__all__ = ["GITHUB_ENTRY"]

GITHUB_ENTRY = McpRegistryEntry(
    name="github",
    description="GitHub MCP server for searching repos, issues, pull requests, and code.",
    repository="https://github.com/modelcontextprotocol/servers.git",
    package="@modelcontextprotocol/server-github",
    default_config=McpStdioServer(
        type="stdio",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": ""},
    ),
)
