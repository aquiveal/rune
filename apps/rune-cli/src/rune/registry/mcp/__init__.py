from rune.registry.mcp.crawl4ai import CRAWL4AI_ENTRY
from rune.registry.mcp.filesystem import FILESYSTEM_ENTRY
from rune.registry.mcp.github import GITHUB_ENTRY
from rune.registry.mcp.memory import MEMORY_ENTRY
from rune.registry.mcp.probe import PROBE_ENTRY
from rune.schemas.mcp_schema import McpRegistryEntry

__all__ = [
    "CRAWL4AI_ENTRY",
    "FILESYSTEM_ENTRY",
    "GITHUB_ENTRY",
    "MEMORY_ENTRY",
    "PROBE_ENTRY",
    "REGISTRY",
    "get_builtin_registry",
    "get_registry",
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
    q = query.lower().strip()
    registry = get_registry()
    seen = set()
    results = []
    for entry in registry.values():
        if entry.name in seen:
            continue
        if (
            q in entry.name.lower()
            or q in entry.description.lower()
            or (entry.package and q in entry.package.lower())
        ):
            seen.add(entry.name)
            results.append(entry)
    return results
