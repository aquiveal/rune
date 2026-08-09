import subprocess
from pathlib import Path

from rune.repositories import mcp_repository
from rune.services import mcp_service


def test_crawl4ai_internal_service_integration_flow(tmp_path: Path, monkeypatch):
    """Internal integration test verifying mcp_service -> mcp_repository -> filesystem config flow."""
    git_root = tmp_path
    (git_root / ".roo").mkdir()
    (git_root / ".claude").mkdir()

    monkeypatch.setattr("shutil.which", lambda x: "/usr/bin/docker")

    executed_commands = []

    def mock_run(cmd, **kwargs):
        executed_commands.append(cmd)
        if "ps" in cmd:
            return subprocess.CompletedProcess(cmd, 0, stdout="crawl4ai\n", stderr="")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr("subprocess.run", mock_run)

    # Execute service integration call across multiple agent targets
    updated_paths = mcp_service.add_mcp_server(
        source="crawl4ai",
        git_root=git_root,
        cwd=git_root,
        global_scope=False,
        agent_override=[".roo", ".claude"],
    )

    assert len(updated_paths) >= 2

    # Verify workspace mcp configurations
    roo_path = git_root / ".roo" / "mcp.json"
    claude_path = git_root / ".claude" / "mcp.json"

    assert roo_path.exists()
    assert claude_path.exists()

    roo_cfg = mcp_repository.load_mcp_config(roo_path)
    claude_cfg = mcp_repository.load_mcp_config(claude_path)

    assert "crawl4ai" in roo_cfg.mcpServers
    assert "crawl4ai" in claude_cfg.mcpServers

    assert roo_cfg.mcpServers["crawl4ai"].type == "sse"
    assert roo_cfg.mcpServers["crawl4ai"].url == "http://localhost:11235/mcp/sse"

    # Verify mcp_service.list_mcp_servers integration retrieval
    servers = mcp_service.list_mcp_servers(git_root, global_scope=False)
    assert "crawl4ai" in servers
    assert servers["crawl4ai"]["config"]["url"] == "http://localhost:11235/mcp/sse"
