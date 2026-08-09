from pathlib import Path

from rune.schemas.mcp_schema import McpStdioServer
from rune.services import mcp_service


def test_builtin_registry():
    registry = mcp_service.get_builtin_registry()
    assert "probe" in registry
    assert "probelabs/probe" in registry
    assert "crawl4ai" in registry
    assert "unclecode/crawl4ai" in registry
    probe_entry = registry["probe"]
    assert probe_entry.name == "probe"
    assert "roo" in probe_entry.agent_configs
    crawl_entry = registry["crawl4ai"]
    assert crawl_entry.name == "crawl4ai"
    assert crawl_entry.default_config.type == "sse"
    assert crawl_entry.default_config.url == "http://localhost:11235/mcp/sse"


def test_ensure_crawl4ai_docker_container_already_running(monkeypatch):
    import subprocess

    def mock_run(cmd, **kwargs):
        if cmd[:3] == ["docker", "ps", "--filter"]:
            return subprocess.CompletedProcess(cmd, 0, stdout="crawl4ai\n", stderr="")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr("shutil.which", lambda x: "/usr/bin/docker")
    monkeypatch.setattr("subprocess.run", mock_run)

    assert mcp_service.ensure_crawl4ai_docker_container() is True


def test_ensure_crawl4ai_docker_container_stopped(monkeypatch):
    import subprocess

    started = []

    def mock_run(cmd, **kwargs):
        if cmd[:3] == ["docker", "ps", "--filter"]:
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
        if cmd[:4] == ["docker", "ps", "-a", "--filter"]:
            return subprocess.CompletedProcess(cmd, 0, stdout="crawl4ai\n", stderr="")
        if cmd[:2] == ["docker", "start"]:
            started.append(cmd)
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr("shutil.which", lambda x: "/usr/bin/docker")
    monkeypatch.setattr("subprocess.run", mock_run)

    assert mcp_service.ensure_crawl4ai_docker_container() is True
    assert len(started) == 1
    assert started[0] == ["docker", "start", "crawl4ai"]


def test_ensure_crawl4ai_docker_container_new(monkeypatch):
    import subprocess

    ran_cmds = []

    def mock_run(cmd, **kwargs):
        ran_cmds.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr("shutil.which", lambda x: "/usr/bin/docker")
    monkeypatch.setattr("subprocess.run", mock_run)

    res = mcp_service.ensure_crawl4ai_docker_container(
        api_token="my-token", model="gemini/gemini-2.0-flash"
    )
    assert res is True
    run_cmd = ran_cmds[-1]
    assert run_cmd[0] == "docker"
    assert run_cmd[1] == "run"
    assert "GEMINI_API_TOKEN=my-token" in run_cmd
    assert "LLM_PROVIDER=gemini/gemini-2.0-flash" in run_cmd


def test_add_crawl4ai_mcp_server(tmp_path: Path, monkeypatch):
    monkeypatch.setattr("shutil.which", lambda x: "/usr/bin/docker")

    import subprocess

    def mock_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, 0, stdout="crawl4ai\n", stderr="")

    monkeypatch.setattr("subprocess.run", mock_run)

    git_root = tmp_path
    (git_root / ".roo").mkdir()
    updated = mcp_service.add_mcp_server(
        source="crawl4ai",
        git_root=git_root,
        cwd=git_root,
        global_scope=False,
    )
    assert len(updated) > 0
    roo_json = git_root / ".roo" / "mcp.json"
    assert roo_json.exists()
    content = roo_json.read_text(encoding="utf-8")
    assert "crawl4ai" in content
    assert "http://localhost:11235/mcp/sse" in content


def test_search_registry():
    results = mcp_service.search_registry("probe")
    assert len(results) >= 1
    assert any(r.name == "probe" for r in results)


def test_add_mcp_server_from_registry(tmp_path: Path):
    git_root = tmp_path
    (git_root / ".roo").mkdir()
    updated = mcp_service.add_mcp_server(
        source="probelabs/probe",
        git_root=git_root,
        cwd=git_root,
        global_scope=False,
    )
    assert len(updated) > 0
    # Check .roo/mcp.json
    roo_json = git_root / ".roo" / "mcp.json"
    assert roo_json.exists()
    content = roo_json.read_text(encoding="utf-8")
    assert "probe" in content


def test_add_custom_stdio_server(tmp_path: Path):
    git_root = tmp_path
    (git_root / ".roo").mkdir()
    custom = McpStdioServer(
        type="stdio",
        command="python",
        args=["-m", "custom_mcp"],
    )
    updated = mcp_service.add_mcp_server(
        source="my-custom-mcp",
        git_root=git_root,
        cwd=git_root,
        global_scope=False,
        custom_config=custom,
    )
    assert len(updated) > 0
    roo_json = git_root / ".roo" / "mcp.json"
    assert roo_json.exists()
    content = roo_json.read_text(encoding="utf-8")
    assert "my-custom-mcp" in content
    assert "custom_mcp" in content


def test_list_and_remove_mcp_servers(tmp_path: Path):
    git_root = tmp_path
    (git_root / ".roo").mkdir()
    mcp_service.add_mcp_server(
        source="probe",
        git_root=git_root,
        cwd=git_root,
        global_scope=False,
    )
    servers = mcp_service.list_mcp_servers(git_root, global_scope=False)
    assert "probe" in servers

    removed = mcp_service.remove_mcp_server(["probe"], git_root, global_scope=False)
    assert len(removed) > 0

    servers_after = mcp_service.list_mcp_servers(git_root, global_scope=False)
    assert "probe" not in servers_after
