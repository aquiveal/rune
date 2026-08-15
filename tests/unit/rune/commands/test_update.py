import subprocess
from unittest.mock import MagicMock, call, patch

from typer.testing import CliRunner

from rune.main import app

runner = CliRunner()


@patch(
    "rune.commands.update.shutil.which",
    return_value="C:\\Users\\user\\.cargo\\bin\\uv.exe",
)
@patch("rune.commands.update.subprocess.run")
def test_rune_update_success(mock_subprocess_run, mock_shutil_which):
    mock_subprocess_run.return_value = MagicMock(returncode=0)

    result = runner.invoke(app, ["update"])
    assert result.exit_code == 0
    assert "Successfully updated Rune CLI." in result.output

    expected_cmd = [
        "uv",
        "tool",
        "install",
        "--python",
        "3.13",
        "--reinstall",
        "git+https://github.com/aquiveal/rune.git",
    ]
    mock_subprocess_run.assert_has_calls([call(expected_cmd, check=True)])


@patch(
    "rune.commands.update.shutil.which",
    return_value="C:\\Users\\user\\.cargo\\bin\\uv.exe",
)
@patch("rune.commands.update.subprocess.run")
def test_rune_update_custom_options(mock_subprocess_run, mock_shutil_which):
    mock_subprocess_run.return_value = MagicMock(returncode=0)

    result = runner.invoke(
        app,
        [
            "update",
            "--python",
            "3.12",
            "--source",
            "git+https://github.com/custom/rune.git",
        ],
    )
    assert result.exit_code == 0
    assert "Successfully updated Rune CLI." in result.output

    expected_cmd = [
        "uv",
        "tool",
        "install",
        "--python",
        "3.12",
        "--reinstall",
        "git+https://github.com/custom/rune.git",
    ]
    mock_subprocess_run.assert_has_calls([call(expected_cmd, check=True)])


@patch("rune.commands.update.shutil.which", return_value=None)
def test_rune_update_missing_uv(mock_shutil_which):
    result = runner.invoke(app, ["update"])
    assert result.exit_code == 1
    assert "was not found in PATH" in result.output or "install uv" in result.output


@patch(
    "rune.commands.update.shutil.which",
    return_value="C:\\Users\\user\\.cargo\\bin\\uv.exe",
)
@patch("rune.commands.update.subprocess.run")
def test_rune_update_process_failure(mock_subprocess_run, mock_shutil_which):
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(
        returncode=2, cmd=["uv", "tool", "install"]
    )

    result = runner.invoke(app, ["update"])
    assert result.exit_code == 2
    assert "Failed to update Rune CLI" in result.output
