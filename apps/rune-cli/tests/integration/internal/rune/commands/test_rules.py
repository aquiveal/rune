import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from rune.main import app
from typer.testing import CliRunner

runner = CliRunner()


def test_rules_add_doc_integration_flow(tmp_path: Path, monkeypatch):
    """Internal integration test verifying rules add <url> <name> -> filesystem & AGENTS.md."""
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)

    # Mock docker checking to pretend Crawl4AI is ready
    def mock_run(cmd, **kwargs):
        if "ps" in cmd:
            return subprocess.CompletedProcess(cmd, 0, stdout="crawl4ai\n", stderr="")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr("subprocess.run", mock_run)

    html_payload = """
    <html>
        <head>
            <title>Amazon Selling Partner API</title>
            <meta name="description" content="Build apps for sellers and vendors worldwide." />
        </head>
        <body>
            <h1>Welcome to SP-API</h1>
            <a href="/sp-api/docs/authorization-and-authentication" title="OAuth and LWA guide">Auth Guide</a>
            <a href="/sp-api/reference/orders-api-v0-reference">Orders API</a>
        </body>
    </html>
    """

    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = html_payload.encode("utf-8")

    with patch("rune.services.rule_service.urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        result = runner.invoke(
            app,
            [
                "rules",
                "add",
                "https://developer-docs.amazon/sp-api/reference/welcome-to-api-references",
                "amazon-sp-api",
                "--agent",
                ".roo",
            ],
        )

    assert result.exit_code == 0

    # Verify rule file written under .roo/rules/amazon-sp-api.md
    rule_file = tmp_path / ".roo" / "rules" / "amazon-sp-api.md"
    assert rule_file.exists()

    content = rule_file.read_text(encoding="utf-8")
    assert "name: amazon-sp-api" in content
    assert "type: documentation" in content
    assert "crawl4ai" in content
    assert "Auth Guide" in content
    assert "OAuth and LWA guide" in content
    assert (
        "https://developer-docs.amazon/sp-api/docs/authorization-and-authentication"
        in content
    )

    # Verify AGENTS.md updated
    agents_md = tmp_path / "AGENTS.md"
    assert agents_md.exists()
    agents_content = agents_md.read_text(encoding="utf-8")
    assert "Amazon Selling Partner API" in agents_content
    assert "Auth Guide" in agents_content
