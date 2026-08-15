from rune.registry.mcp import crawl4ai, filesystem, github, memory, probe
from rune.registry.mcp.crawl4ai import (
    CRAWL4AI_ENTRY,
    init_crawl4ai,
)
from rune.registry.mcp.filesystem import (
    FILESYSTEM_ENTRY,
)
from rune.registry.mcp.github import (
    GITHUB_ENTRY,
)
from rune.registry.mcp.memory import (
    MEMORY_ENTRY,
)
from rune.registry.mcp.probe import (
    PROBE_ALLOW,
    PROBE_ENTRY,
)
from rune.schemas.mcp_schema import McpRegistryEntry

__all__ = [
    "CRAWL4AI_ENTRY",
    "FILESYSTEM_ENTRY",
    "GITHUB_ENTRY",
    "MEMORY_ENTRY",
    "PROBE_ALLOW",
    "PROBE_ENTRY",
    "REGISTRY",
    "crawl4ai",
    "filesystem",
    "get_builtin_registry",
    "get_registry",
    "github",
    "init_crawl4ai",
    "memory",
    "probe",
    "search_registry",
]

REGISTRY: dict[str, McpRegistryEntry] = {
    "probe": PROBE_ENTRY,
    "probelabs/probe": PROBE_ENTRY,
    "filesystem": FILESYSTEM_ENTRY,
    "github": GITHUB_ENTRY,
    "memory": MEMORY_ENTRY,
    "crawl4ai": CRAWL4AI_ENTRY,
    "unclecode/crawl4ai": CRAWL4AI_ENTRY,
}


def get_registry() -> dict[str, McpRegistryEntry]:
    """Return the built-in MCP server registry dictionary."""
    return REGISTRY


def get_builtin_registry() -> dict[str, McpRegistryEntry]:
    """Alias for get_registry()."""
    return get_registry()


def search_registry(query: str) -> list[McpRegistryEntry]:
    """Search for MCP registry entries matching query."""
    q = query.lower()
    matched_entries: list[McpRegistryEntry] = []
    seen_names: set[str] = set()
    for key, entry in REGISTRY.items():
        if entry.name in seen_names:
            continue
        if (
            q in key.lower()
            or (entry.description and q in entry.description.lower())
            or q in entry.name.lower()
        ):
            matched_entries.append(entry)
            seen_names.add(entry.name)
    return matched_entries
