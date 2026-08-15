import os
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from rune.main import app
from rune.repositories import mcp_repository
from rune.schemas.mcp_schema import McpStdioServer

runner = CliRunner()


def test_e2e_mcp_add_preserves_always_allow_permissions(tmp_path: Path):
    """E2E test verifying that adding or updating an MCP server preserves existing alwaysAllow tool permissions."""
    os.chdir(tmp_path)
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)

    roo_dir = tmp_path / ".roo"
    roo_dir.mkdir(parents=True)
    mcp_json_path = roo_dir / "mcp.json"

    # Pre-populate mcp.json with custom alwaysAllow tool permissions and env variables
    existing_cfg = mcp_repository.load_mcp_config(mcp_json_path)
    existing_cfg.mcpServers["probe"] = McpStdioServer(
        type="stdio",
        command="npx",
        args=["-y", "@probelabs/probe@latest", "agent", "--mcp"],
        alwaysAllow=["search_code", "extract_code", "my_custom_tool"],
        env={"EXISTING_ENV_KEY": "12345"},
    )
    mcp_repository.save_mcp_config(mcp_json_path, existing_cfg)

    # Invoke CLI to add/update probe
    res = runner.invoke(app, ["mcp", "add", "probe", "--agent", ".roo"])
    assert res.exit_code == 0

    # Read back mcp.json and assert alwaysAllow tools and env keys were merged & preserved
    loaded_cfg = mcp_repository.load_mcp_config(mcp_json_path)
    assert "probe" in loaded_cfg.mcpServers
    probe_srv = loaded_cfg.mcpServers["probe"]

    assert "search_code" in probe_srv.alwaysAllow
    assert "extract_code" in probe_srv.alwaysAllow
    assert "my_custom_tool" in probe_srv.alwaysAllow
    assert "probe_search" in probe_srv.alwaysAllow
    assert probe_srv.env.get("EXISTING_ENV_KEY") == "12345"
