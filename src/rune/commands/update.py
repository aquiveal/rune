# src/rune/commands/update.py
import shutil
import subprocess

import structlog
import typer

__all__ = ["update_cmd"]

logger = structlog.get_logger(__name__)


def update_cmd(
    python_version: str = typer.Option(
        "3.13",
        "--python",
        "-p",
        help="Python version to use for tool installation",
    ),
    repo_url: str = typer.Option(
        "git+https://github.com/aquiveal/rune.git",
        "--source",
        "-s",
        help="Repository URL or package source to install from",
    ),
):
    """Reinstall and update Rune CLI to the latest version using uv."""
    uv_path = shutil.which("uv")
    if not uv_path:
        err_msg = "`uv` was not found in PATH. Please install uv (https://docs.astral.sh/uv/) or update manually using pipx."
        logger.error(err_msg)
        typer.echo(f"Error: {err_msg}")
        raise typer.Exit(1)

    cmd = [
        "uv",
        "tool",
        "install",
        "--python",
        python_version,
        "--reinstall",
        repo_url,
    ]
    logger.info("Updating Rune CLI via uv...", command=" ".join(cmd))
    typer.echo(f"Updating Rune CLI via uv ({' '.join(cmd)})...")
    try:
        subprocess.run(cmd, check=True)
        typer.echo("Successfully updated Rune CLI.")
    except subprocess.CalledProcessError as e:
        logger.error("Failed to update Rune CLI", error=str(e))
        typer.echo(f"Failed to update Rune CLI: {e}")
        raise typer.Exit(e.returncode)
