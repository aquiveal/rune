import os
import subprocess
from pathlib import Path

from rune.main import app
from typer.testing import CliRunner

runner = CliRunner()


def test_crawl4ai_mcp_e2e_setup_and_usability(tmp_path: Path, monkeypatch):
    """End-to-End setup and usability test for Crawl4AI MCP integration."""
    os.chdir(tmp_path)
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)

    monkeypatch.setattr("shutil.which", lambda x: "/usr/bin/docker")

    docker_invocations = []

    def mock_run(cmd, **kwargs):
        docker_invocations.append(cmd)
        if "ps" in cmd:
            return subprocess.CompletedProcess(cmd, 0, stdout="crawl4ai\n", stderr="")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr("subprocess.run", mock_run)

    # Step 1: E2E Setup via CLI
    res = runner.invoke(
        app,
        ["mcp", "add", "crawl4ai", "--agent", ".roo"],
    )
    assert res.exit_code == 0

    # Step 2: Validate generated config structure
    mcp_config_path = tmp_path / ".roo" / "mcp.json"
    assert mcp_config_path.exists()

    content = mcp_config_path.read_text(encoding="utf-8")
    assert "crawl4ai" in content
    assert "mcp-crawl4ai-ts" in content
    assert "http://localhost:11235" in content

    # Step 3: Validate Usability - Docker readiness check was triggered
    assert len(docker_invocations) > 0
    assert any("docker" in cmd[0] for cmd in docker_invocations)

    # Step 4: Validate MCP List CLI integration
    res_list = runner.invoke(app, ["mcp", "list"])
    assert res_list.exit_code == 0
    assert "crawl4ai" in res_list.stdout.lower()
