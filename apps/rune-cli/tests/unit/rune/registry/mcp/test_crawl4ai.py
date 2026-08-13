import subprocess

from rune.registry.mcp.crawl4ai import CRAWL4AI_ENTRY, init_crawl4ai


def test_crawl4ai_entry():
    assert CRAWL4AI_ENTRY.name == "crawl4ai"
    assert CRAWL4AI_ENTRY.package == "mcp-crawl4ai-ts"
    assert CRAWL4AI_ENTRY.default_config is not None
    assert CRAWL4AI_ENTRY.init == init_crawl4ai


def test_init_crawl4ai_already_running(monkeypatch):
    def mock_run(cmd, **kwargs):
        if cmd[:3] == ["docker", "ps", "--filter"]:
            return subprocess.CompletedProcess(cmd, 0, stdout="crawl4ai\n", stderr="")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr("shutil.which", lambda x: "/usr/bin/docker")
    monkeypatch.setattr("subprocess.run", mock_run)

    assert init_crawl4ai() is True
