from unittest.mock import patch

from rune.repositories import config_repository, index_repository
from rune.services import submodule_service, workspace_service


def test_submodule_discovery_and_upward_merging(tmp_path):
    # Initialize parent workspace
    workspace_service.init_workspace(tmp_path)

    # Set up a submodule directory manually
    sub_dir = tmp_path / "submodules" / "frontend"
    sub_dir.mkdir(parents=True)

    # Create a rule and skill in submodule agent folder
    sub_agent_dir = sub_dir / ".agents"
    sub_skills_dir = sub_agent_dir / "skills" / "sub-skill"
    sub_skills_dir.mkdir(parents=True)
    (sub_skills_dir / "SKILL.md").write_text(
        "---\nname: sub-skill\ndescription: Submodule skill\n---\n# Sub skill\n"
    )

    sub_rules_dir = sub_agent_dir / "rules"
    sub_rules_dir.mkdir(parents=True)
    (sub_rules_dir / "sub-rule.md").write_text("# Submodule Rule\nCustom rule content.")

    # Explicitly configure submodule.path
    config_repository.add_submodule_path(tmp_path, "submodules/frontend")
    with patch("rune.config.main.settings.submodules", ["submodules/frontend"]):
        # Merge upward to workspace
        submodule_service.merge_submodules_upward_to_workspace(tmp_path)

        # Assert skill and rule merged into parent workspace agent folder
        parent_skill = tmp_path / ".agents" / "skills" / "sub-skill"
        assert parent_skill.exists()

        parent_rule = tmp_path / ".agents" / "rules" / "sub-rule.md"
        assert parent_rule.exists()

        # Assert provenance index recorded the item
        index_items = index_repository.get_items_by_scope(
            tmp_path, "submodule:submodules/frontend"
        )
        assert len(index_items) >= 1
