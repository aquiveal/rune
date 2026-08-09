from rune.repositories import mcp_repository
from rune.services import mcp_service


def test_probe_mcp_api_key_preservation(tmp_path):
    # Set up mock MCP config with existing API key
    agent_dir = tmp_path / ".agents"
    agent_dir.mkdir(parents=True)
    mcp_path = agent_dir / "mcp.json"

    initial_cfg = mcp_repository.load_mcp_config(mcp_path)
    from rune.schemas.mcp_schema import McpStdioServer

    initial_cfg.mcpServers["probe"] = McpStdioServer(
        type="stdio",
        command="npx",
        args=["-y", "@probelabs/probe@latest", "agent", "--mcp"],
        env={"GOOGLE_GENERATIVE_AI_API_KEY": "PRESERVED_KEY_123"},
    )
    mcp_repository.save_mcp_config(mcp_path, initial_cfg)

    # Re-run add_mcp_server
    mcp_service.add_mcp_server(
        "probelabs/probe",
        git_root=tmp_path,
        cwd=tmp_path,
        global_scope=False,
        agent_override=[".agents"],
    )

    # Assert key was preserved
    updated_cfg = mcp_repository.load_mcp_config(mcp_path)
    assert "probe" in updated_cfg.mcpServers
    probe_server = updated_cfg.mcpServers["probe"]
    assert probe_server.env["GOOGLE_GENERATIVE_AI_API_KEY"] == "PRESERVED_KEY_123"
