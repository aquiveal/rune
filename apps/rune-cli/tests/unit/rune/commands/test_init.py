import os

from rune.main import app
from typer.testing import CliRunner

runner = CliRunner()


def test_init(tmp_path):
    os.chdir(tmp_path)
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert (tmp_path / ".rune").is_dir()
    assert (tmp_path / ".runemodules").exists()
