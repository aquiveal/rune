import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from rune.main import app

runner = CliRunner()


def test_rules_doc_crawl_e2e_workflow(tmp_path: Path, monkeypatch):
    """End-to-End full user workflow test for documentation rule creation and live Crawl4AI integration."""
    os.chdir(tmp_path)

    # 1. Initialize empty Rune workspace
    res_init = runner.invoke(app, ["init"])
    assert res_init.exit_code == 0
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)

    # 2. Mock Docker readiness check
    monkeypatch.setattr("shutil.which", lambda x: "/usr/bin/docker")

    docker_invocations = []

    def mock_run(cmd, **kwargs):
        docker_invocations.append(cmd)
        if "ps" in cmd:
            return subprocess.CompletedProcess(cmd, 0, stdout="crawl4ai\n", stderr="")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr("subprocess.run", mock_run)

    html_payload = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Amazon Selling Partner API</title>
            <meta name="description" content="Official Amazon SP-API documentation and reference" />
        </head>
        <body>
            <h1>Amazon SP-API Reference</h1>
            <a href="/sp-api/reference/orders" title="Manage orders endpoints">Orders API</a>
            <a href="/sp-api/reference/reports" title="Manage report downloads">Reports API</a>
        </body>
    </html>
    """

    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = html_payload.encode("utf-8")

    with (
        patch("rune.services.rule_service.urllib.request.urlopen") as mock_urlopen,
        patch(
            "rune.repositories.mcp_repository.is_server_configured_globally",
            return_value=False,
        ),
    ):
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        # 3. Execute rune rules add <url> <name>
        res_add = runner.invoke(
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

    assert res_add.exit_code == 0

    # 4. Verify generated rule file
    rule_file = tmp_path / ".roo" / "rules" / "amazon-sp-api.md"
    assert rule_file.exists()

    content = rule_file.read_text(encoding="utf-8")
    assert "name: amazon-sp-api" in content
    assert "type: documentation" in content
    assert "crawl4ai" in content
    assert "Orders API" in content
    assert "Manage orders endpoints" in content
    assert "https://developer-docs.amazon/sp-api/reference/orders" in content
    assert "https://developer-docs.amazon/sp-api/reference/reports" in content

    # 5. Verify MCP configuration updated for Crawl4AI
    mcp_config = tmp_path / ".roo" / "mcp.json"
    assert mcp_config.exists()
    assert "crawl4ai" in mcp_config.read_text(encoding="utf-8")

    # 6. Verify AGENTS.md updated
    agents_md = tmp_path / "AGENTS.md"
    assert agents_md.exists()
    agents_text = agents_md.read_text(encoding="utf-8")
    assert "Amazon Selling Partner API" in agents_text
    assert "Orders API" in agents_text

    # 7. Verify rules list CLI
    res_list = runner.invoke(app, ["rules", "list"])
    assert res_list.exit_code == 0
