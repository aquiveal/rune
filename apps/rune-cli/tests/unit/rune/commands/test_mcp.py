import os
import subprocess
from pathlib import Path

from rune.main import app
from typer.testing import CliRunner

runner = CliRunner()


def test_mcp_help():
    result = runner.invoke(app, ["mcp", "--help"])
    assert result.exit_code == 0
    assert "Manage Model Context Protocol" in result.stdout


def test_mcp_registry_command():
    result = runner.invoke(app, ["mcp", "registry", "probe"])
    assert result.exit_code == 0
    assert "probe" in result.stdout.lower()


def test_mcp_add_and_list(tmp_path: Path):
    os.chdir(tmp_path)
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)

    result_add = runner.invoke(
        app, ["mcp", "add", "probelabs/probe", "--agent", ".roo"]
    )
    assert result_add.exit_code == 0

    result_list = runner.invoke(app, ["mcp", "list"])
    assert result_list.exit_code == 0
    assert "probe" in result_list.stdout.lower()


def test_mcp_validate_valid_file(tmp_path: Path):
    os.chdir(tmp_path)
    mcp_json = tmp_path / "mcp.json"
    mcp_json.write_text(
        '{"mcpServers": {"test": {"type": "stdio", "command": "echo"}}}',
        encoding="utf-8",
    )
    result = runner.invoke(app, ["mcp", "validate", str(mcp_json)])
    assert result.exit_code == 0
    assert "valid" in result.stdout.lower()


def test_mcp_remove_command(tmp_path: Path):
    os.chdir(tmp_path)
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)
    runner.invoke(app, ["mcp", "add", "probelabs/probe", "--agent", ".roo"])

    result_rm = runner.invoke(app, ["mcp", "remove", "probe"])
    assert result_rm.exit_code == 0

    result_list = runner.invoke(app, ["mcp", "list"])
    assert "probe" not in result_list.stdout.lower()
