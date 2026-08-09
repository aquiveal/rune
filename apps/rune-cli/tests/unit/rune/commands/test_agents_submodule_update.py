import os
from unittest.mock import patch

from typer.testing import CliRunner

from rune.main import app
from rune.repositories import config_repository

runner = CliRunner()


def test_agents_update_3_step_sequence(tmp_path):
    os.chdir(tmp_path)
    runner.invoke(app, ["init"])

    # Create submodule structure
    sub_dir = tmp_path / "submodules" / "backend"
    sub_dir.mkdir(parents=True)
    sub_agent = sub_dir / ".agents" / "skills" / "back-skill"
    sub_agent.mkdir(parents=True)
    (sub_agent / "SKILL.md").write_text(
        "---\nname: back-skill\ndescription: Backend skill\n---\n# Back skill\n"
    )

    config_repository.add_submodule_path(tmp_path, "submodules/backend")

    with patch("rune.config.main.settings.submodules", ["submodules/backend"]):
        result = runner.invoke(app, ["agents", "update"])
        assert result.exit_code == 0

        # Check upward merge result in parent workspace
        merged_skill = tmp_path / ".agents" / "skills" / "back-skill"
        assert merged_skill.exists()
