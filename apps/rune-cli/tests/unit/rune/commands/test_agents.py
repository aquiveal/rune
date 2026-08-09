from unittest.mock import MagicMock, call, patch

from typer.testing import CliRunner

from rune.main import app

runner = CliRunner()


@patch("rune.commands.agents.mcp_service.add_mcp_server")
@patch("rune.commands.agents.module_service.update_modules")
@patch("rune.commands.agents.rule_service.discover_rule_dirs")
@patch("rune.commands.agents.git_repository.update_submodules")
@patch("rune.commands.agents.skill_service.discover_skills")
@patch("rune.commands.agents.skill_service.update_skill_instructions")
@patch("rune.commands.agents.rule_service.merge_rules_to_agents_md")
@patch("rune.commands.agents.map_service.generate_submodule_map")
@patch("rune.commands.agents.map_service.merge_ast_to_agents_md")
@patch("rune.commands.agents.git_repository.get_git_root")
@patch("rune.commands.agents.Path.cwd")
def test_agents_update_success(
    mock_cwd,
    mock_get_git_root,
    mock_merge_ast,
    mock_gen_map,
    mock_merge_rules,
    mock_update_skill_instructions,
    mock_discover_skills,
    mock_update_submodules,
    mock_discover_rule_dirs,
    mock_update_modules,
    mock_add_mcp,
):
    # Arrange
    mock_cwd_path = MagicMock()
    mock_cwd.return_value = mock_cwd_path
    mock_get_git_root.return_value = mock_cwd_path

    mock_rule_dir = MagicMock()
    mock_rule_dir.__truediv__.return_value.exists.return_value = True
    mock_discover_rule_dirs.return_value = [mock_rule_dir]

    mock_skill = MagicMock()
    mock_skill.path = "skills/my-skill"
    mock_discover_skills.return_value = [mock_skill]

    mock_gen_map.return_value = "mock_ast"

    # Act
    result = runner.invoke(app, ["agents", "update"])

    # Assert
    assert result.exit_code == 0

    mock_update_modules.assert_has_calls(
        [
            call(mock_cwd_path, type="rules", global_scope=False),
            call(mock_cwd_path, type="skills", global_scope=False),
            call(mock_cwd_path, type="modules", global_scope=False),
        ]
    )
    mock_update_submodules.assert_called_once_with(mock_rule_dir)
    mock_update_skill_instructions.assert_called_once()
    mock_merge_rules.assert_called_once_with(mock_cwd_path)
    mock_gen_map.assert_called_once_with(mock_cwd_path)
    mock_merge_ast.assert_called_once_with(mock_cwd_path, "mock_ast")


@patch("rune.commands.agents.mcp_service.add_mcp_server")
@patch("rune.commands.agents.module_service.update_modules")
@patch("rune.commands.agents.rule_service.discover_rule_dirs")
@patch("rune.commands.agents.skill_service.discover_skills")
@patch("rune.commands.agents.skill_service.update_skill_instructions")
@patch("rune.commands.agents.rule_service.merge_rules_to_agents_md")
@patch("rune.commands.agents.map_service.generate_submodule_map")
@patch("rune.commands.agents.map_service.merge_ast_to_agents_md")
@patch("rune.commands.agents.git_repository.get_git_root")
@patch("rune.commands.agents.Path.cwd")
def test_agents_update_continues_on_rule_failure(
    mock_cwd,
    mock_get_git_root,
    mock_merge_ast,
    mock_gen_map,
    mock_merge_rules,
    mock_update_skill_instructions,
    mock_discover_skills,
    mock_discover_rule_dirs,
    mock_update_modules,
    mock_add_mcp,
):
    # Arrange
    mock_cwd_path = MagicMock()
    mock_cwd.return_value = mock_cwd_path
    mock_get_git_root.return_value = mock_cwd_path

    def update_modules_side_effect(path, type, global_scope):
        if type == "rules":
            raise RuntimeError("Rule update failed")

    mock_update_modules.side_effect = update_modules_side_effect

    mock_skill = MagicMock()
    mock_skill.path = "skills/my-skill"
    mock_discover_skills.return_value = [mock_skill]

    mock_gen_map.return_value = "mock_ast"

    # Act
    result = runner.invoke(app, ["agents", "update"])

    # Assert
    assert result.exit_code == 0

    mock_discover_skills.assert_called_once()
    mock_update_skill_instructions.assert_called_once()
    mock_merge_rules.assert_called_once()
    mock_gen_map.assert_called_once()
    mock_merge_ast.assert_called_once()
