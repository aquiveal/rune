import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from rune.services import rule_service


def test_rule_service_create_rule_from_doc_url_integration(tmp_path: Path, monkeypatch):
    """Direct service integration test for create_rule_from_doc_url."""
    os.chdir(tmp_path)
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)

    # Mock docker checking
    def mock_run(cmd, **kwargs):
        if "ps" in cmd:
            return subprocess.CompletedProcess(cmd, 0, stdout="crawl4ai\n", stderr="")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr("subprocess.run", mock_run)

    html_payload = """
    <html>
        <head>
            <title>FastAPI Documentation</title>
            <meta name="description" content="FastAPI high-performance web framework" />
        </head>
        <body>
            <h1>FastAPI Tutorial</h1>
            <a href="/tutorial/body" title="Request body handling">Request Body</a>
            <a href="/tutorial/query-params">Query Params</a>
        </body>
    </html>
    """

    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = html_payload.encode("utf-8")

    with patch("rune.services.rule_service.urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        rule_path = rule_service.create_rule_from_doc_url(
            url="https://fastapi.tiangolo.com/tutorial",
            name="fastapi-docs",
            git_root=tmp_path,
            cwd=tmp_path,
            target_agents=[".agents"],
            global_scope=False,
        )

    assert rule_path.exists()
    assert rule_path.name == "fastapi-docs.md"

    content = rule_path.read_text(encoding="utf-8")
    assert "name: fastapi-docs" in content
    assert "FastAPI high-performance web framework" in content
    assert "Request Body" in content
    assert "https://fastapi.tiangolo.com/tutorial/body" in content

    # Check AGENTS.md updated
    agents_md = tmp_path / "AGENTS.md"
    assert agents_md.exists()
    assert "FastAPI Documentation" in agents_md.read_text()
    assert "FastAPI high-performance web framework" in agents_md.read_text()
