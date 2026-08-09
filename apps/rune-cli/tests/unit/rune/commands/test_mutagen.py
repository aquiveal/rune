import os

import yaml
from typer.testing import CliRunner

from rune.main import app

runner = CliRunner()


def test_mutagen_update_command_success(tmp_path):
    os.chdir(tmp_path)
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("*.log\nnode_modules/\n", encoding="utf-8")

    mutagen = tmp_path / "mutagen.yml"
    mutagen.write_text(yaml.dump({"sync": {}}, sort_keys=False), encoding="utf-8")

    result = runner.invoke(app, ["mutagen", "update"])
    assert result.exit_code == 0

    data = yaml.safe_load(mutagen.read_text(encoding="utf-8"))
    assert data["sync"]["defaults"]["ignore"]["paths"] == ["*.log", "node_modules/"]


def test_mutagen_update_command_with_options(tmp_path):
    os.chdir(tmp_path)
    custom_gitignore = tmp_path / ".gitignore_custom"
    custom_gitignore.write_text("dist/\n", encoding="utf-8")

    custom_mutagen = tmp_path / "mutagen_custom.yml"
    custom_mutagen.write_text(yaml.dump({"sync": {}}, sort_keys=False), encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "mutagen",
            "update",
            "--gitignore",
            str(custom_gitignore),
            "--mutagen",
            str(custom_mutagen),
        ],
    )
    assert result.exit_code == 0

    data = yaml.safe_load(custom_mutagen.read_text(encoding="utf-8"))
    assert data["sync"]["defaults"]["ignore"]["paths"] == ["dist/"]


def test_mutagen_update_command_missing_mutagen(tmp_path):
    os.chdir(tmp_path)
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("*.log\n", encoding="utf-8")

    result = runner.invoke(app, ["mutagen", "update"])
    assert result.exit_code == 1
