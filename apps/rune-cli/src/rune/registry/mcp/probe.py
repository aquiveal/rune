from rune.schemas.mcp_schema import McpRegistryEntry, McpStdioServer

__all__ = ["PROBE_ALLOW", "PROBE_ENTRY"]

PROBE_ALLOW = [
    "search_code",
    "extract_code",
    "probe_search",
    "probe_extract",
    "probe_query",
    "probe_symbols",
]

PROBE_ENTRY = McpRegistryEntry(
    name="probe",
    description="Probe is a code and markdown context engine with a built-in agent, made to work on enterprise-scale codebases.",
    repository="https://github.com/probelabs/probe.git",
    package="@probelabs/probe",
    agent_configs={
        "roo": McpStdioServer(
            type="stdio",
            command="npx",
            args=["-y", "@probelabs/probe@latest", "agent", "--mcp"],
            alwaysAllow=PROBE_ALLOW,
        ),
        "cline": McpStdioServer(
            type="stdio",
            command="npx",
            args=["-y", "@probelabs/probe@latest", "agent", "--mcp"],
            alwaysAllow=PROBE_ALLOW,
        ),
        "claude": McpStdioServer(
            type="stdio",
            command="npx",
            args=["-y", "@probelabs/probe@latest", "agent", "--mcp"],
            alwaysAllow=PROBE_ALLOW,
        ),
        "cursor": McpStdioServer(
            type="stdio",
            command="npx",
            args=["-y", "@probelabs/probe@latest", "mcp"],
            alwaysAllow=PROBE_ALLOW,
        ),
        "agents": McpStdioServer(
            type="stdio",
            command="npx",
            args=["-y", "@probelabs/probe@latest", "agent", "--mcp"],
            alwaysAllow=PROBE_ALLOW,
        ),
    },
    default_config=McpStdioServer(
        type="stdio",
        command="npx",
        args=["-y", "@probelabs/probe@latest", "agent", "--mcp"],
        alwaysAllow=PROBE_ALLOW,
    ),
)
