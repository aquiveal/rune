from rune.registry import (
    REGISTRY,
    get_builtin_registry,
    get_registry,
    search_registry,
)


def test_registry_dictionary():
    assert "probe" in REGISTRY
    assert "probelabs/probe" in REGISTRY
    assert "crawl4ai" in REGISTRY
    assert "unclecode/crawl4ai" in REGISTRY
    assert "filesystem" in REGISTRY
    assert "github" in REGISTRY
    assert "memory" in REGISTRY


def test_get_registry():
    reg = get_registry()
    assert reg is REGISTRY
    builtin_reg = get_builtin_registry()
    assert builtin_reg is REGISTRY


def test_search_registry():
    results = search_registry("probe")
    assert len(results) == 1
    assert results[0].name == "probe"

    crawl_results = search_registry("crawl")
    assert len(crawl_results) == 1
    assert crawl_results[0].name == "crawl4ai"

    no_match = search_registry("nonexistent_mcp_server_12345")
    assert len(no_match) == 0
