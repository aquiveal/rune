import os
from unittest import mock


def test_settings_initialization_with_extra_kwargs():
    from rune.config.main import Settings

    with mock.patch.dict(os.environ, {"RANDOM_UNKNOWN_VAR": "test"}, clear=True):
        settings = Settings()
        assert settings.model_config.get("extra") == "ignore"


def test_agent_paths_and_search_helpers():
    from rune.config.main import Settings

    settings = Settings()

    # Check default agent paths
    assert ".agents" in settings.agent_paths
    assert ".roo" in settings.agent_paths
    assert ".claude" in settings.agent_paths
    assert ".cursor" in settings.agent_paths
    assert ".cline" in settings.agent_paths

    # Test get_agent lookup
    roo_agent = settings.get_agent("roo")
    assert roo_agent is not None
    assert roo_agent.workspace.skills == ".roo/skills"
    assert roo_agent.workspace.rules == ".roo/rules"
    assert roo_agent.workspace.mcp == ".roo/mcp.json"
    assert roo_agent.global_scope.skills == ".roo/skills"

    # Test search path helpers
    skill_paths = settings.get_skill_search_paths()
    assert "skills" in skill_paths
    assert ".agents/skills" in skill_paths
    assert ".roo/skills" in skill_paths

    rule_paths = settings.get_rule_search_paths()
    assert "rules" in rule_paths
    assert ".agents/rules" in rule_paths
    assert ".roo/rules" in rule_paths

    mcp_paths_workspace = settings.get_mcp_search_paths(global_scope=False)
    assert mcp_paths_workspace["roo"] == ".roo/mcp.json"
    assert mcp_paths_workspace["agents"] == ".agents/mcp.json"

    mcp_paths_global = settings.get_mcp_search_paths(global_scope=True)
    assert "roo" in mcp_paths_global
    assert "agents" in mcp_paths_global


def test_submodule_and_agent_array_settings():
    from rune.config.main import AgentSettings, Settings, SubmoduleSettings

    sub_cfg = SubmoduleSettings(path=["apps/web", "apps/api"])
    assert sub_cfg.path == ["apps/web", "apps/api"]
    assert sub_cfg.paths == ["apps/web", "apps/api"]

    agent_cfg = AgentSettings(name=[".roo", ".cursor"])
    assert agent_cfg.name == [".roo", ".cursor"]
    assert agent_cfg.names == [".roo", ".cursor"]

    settings = Settings(
        agent=agent_cfg,
        submodule=sub_cfg,
    )
    assert settings.submodules == ["apps/web", "apps/api"]
    assert settings.agent.names == [".roo", ".cursor"]
