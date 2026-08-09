import os
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from rune.main import app

runner = CliRunner()


def test_cli_mcp_crawl4ai_internal_integration(tmp_path: Path, monkeypatch):
    """Internal CLI integration test for crawl4ai mcp commands."""
    os.chdir(tmp_path)
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)

    monkeypatch.setattr("shutil.which", lambda x: "/usr/bin/docker")

    def mock_run(cmd, **kwargs):
        if "ps" in cmd:
            return subprocess.CompletedProcess(cmd, 0, stdout="crawl4ai\n", stderr="")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr("subprocess.run", mock_run)

    # Add crawl4ai via CLI
    res_add = runner.invoke(app, ["mcp", "add", "crawl4ai", "--agent", ".roo"])
    assert res_add.exit_code == 0
    assert (
        "Successfully added MCP server 'crawl4ai'" in res_add.stdout
        or "crawl4ai" in res_add.stdout
    )

    # List MCP servers via CLI
    res_list = runner.invoke(app, ["mcp", "list"])
    assert res_list.exit_code == 0
    assert "crawl4ai" in res_list.stdout.lower()

    # Validate generated mcp.json via CLI
    mcp_json_path = tmp_path / ".roo" / "mcp.json"
    assert mcp_json_path.exists()

    res_val = runner.invoke(app, ["mcp", "validate", str(mcp_json_path)])
    assert res_val.exit_code == 0
    assert "valid" in res_val.stdout.lower()
