import os
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from rune.main import app

runner = CliRunner()


def test_mcp_help():
    result = runner.invoke(app, ["mcp", "--help"])
    assert result.exit_code == 0
    assert "Manage Model Context Protocol" in result.stdout


def test_mcp_registry_command():
    result = runner.invoke(app, ["mcp", "registry", "probe"])
    assert result.exit_code == 0
    assert "probe" in result.stdout.lower()

    result_crawl = runner.invoke(app, ["mcp", "registry", "crawl4ai"])
    assert result_crawl.exit_code == 0
    assert "crawl4ai" in result_crawl.stdout.lower()


def test_mcp_add_and_list_crawl4ai(tmp_path: Path, monkeypatch):
    os.chdir(tmp_path)
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)

    monkeypatch.setattr("shutil.which", lambda x: "/usr/bin/docker")

    def mock_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, 0, stdout="crawl4ai\n", stderr="")

    monkeypatch.setattr("subprocess.run", mock_run)

    result_add = runner.invoke(app, ["mcp", "add", "crawl4ai", "--agent", ".roo"])
    assert result_add.exit_code == 0

    result_list = runner.invoke(app, ["mcp", "list"])
    assert result_list.exit_code == 0
    assert "crawl4ai" in result_list.stdout.lower()


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
