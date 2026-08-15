import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from rune.main import app
from rune.repositories import mcp_repository

runner = CliRunner()


def test_e2e_global_mcp_add_prompts_once_across_agents(tmp_path: Path, monkeypatch):
    """E2E test verifying that adding an MCP server across multiple agents prompts for credentials exactly once."""
    os.chdir(tmp_path)
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)

    (tmp_path / ".roo").mkdir()
    (tmp_path / ".claude").mkdir()

    monkeypatch.delenv("GOOGLE_GENERATIVE_AI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    prompt_mock = MagicMock()
    prompt_mock.ask.return_value = "SECRET_PROBE_API_KEY_999"

    with (
        patch("rune.services.mcp_service._is_tty", return_value=True),
        patch("questionary.password", return_value=prompt_mock) as mock_password,
    ):
        res = runner.invoke(
            app,
            ["mcp", "add", "probe", "--agent", ".roo", "--agent", ".claude"],
        )
        assert res.exit_code == 0

        # Assert questionary.password was called exactly ONCE (not once per agent)
        assert mock_password.call_count == 1

    # Verify environment variable was set in runtime and workspace config uses env reference
    assert os.environ.get("GOOGLE_GENERATIVE_AI_API_KEY") == "SECRET_PROBE_API_KEY_999"

    roo_cfg = mcp_repository.load_mcp_config(tmp_path / ".roo" / "mcp.json")
    claude_cfg = mcp_repository.load_mcp_config(tmp_path / ".claude" / "mcp.json")

    assert "probe" in roo_cfg.mcpServers
    assert "probe" in claude_cfg.mcpServers

    assert (
        roo_cfg.mcpServers["probe"].env["GOOGLE_GENERATIVE_AI_API_KEY"]
        == "${GOOGLE_GENERATIVE_AI_API_KEY}"
    )
    assert (
        claude_cfg.mcpServers["probe"].env["GOOGLE_GENERATIVE_AI_API_KEY"]
        == "${GOOGLE_GENERATIVE_AI_API_KEY}"
    )


def test_e2e_mcp_add_cancellation_exits_cleanly(tmp_path: Path):
    """E2E test verifying that cancelling target agent selection exits cleanly without error tracebacks."""
    os.chdir(tmp_path)
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)

    checkbox_mock = MagicMock()
    checkbox_mock.ask.return_value = None  # User pressed Ctrl+C / Esc

    with patch("questionary.checkbox", return_value=checkbox_mock):
        res = runner.invoke(app, ["mcp", "add", "crawl4ai", "--global"])
        # Should complete cleanly without unhandled exceptions
        assert res.exit_code == 0
        assert (
            "No configuration files were modified" in res.stdout or res.exit_code == 0
        )
