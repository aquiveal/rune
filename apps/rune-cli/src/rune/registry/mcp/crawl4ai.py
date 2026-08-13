import shutil
import subprocess

import structlog

from rune.schemas.mcp_schema import McpRegistryEntry, McpStdioServer

__all__ = ["CRAWL4AI_ENTRY", "init_crawl4ai"]

logger = structlog.get_logger(__name__)


def init_crawl4ai(
    api_token: str | None = None, model: str | None = None
) -> bool:
    """Ensure Crawl4AI Docker container is running on port 11235."""
    if not shutil.which("docker"):
        logger.warning(
            "Docker CLI is not installed or not in PATH. "
            "Please run Crawl4AI container manually: "
            "docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g unclecode/crawl4ai:latest"
        )
        return False

    try:
        ps_proc = subprocess.run(
            ["docker", "ps", "--filter", "name=^crawl4ai$", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=False,
        )
        if "crawl4ai" in ps_proc.stdout:
            logger.info(
                "Crawl4AI Docker container 'crawl4ai' is running on port 11235."
            )
            return True

        ps_all_proc = subprocess.run(
            [
                "docker",
                "ps",
                "-a",
                "--filter",
                "name=^crawl4ai$",
                "--format",
                "{{.Names}}",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if "crawl4ai" in ps_all_proc.stdout:
            logger.info("Starting existing Crawl4AI Docker container...")
            subprocess.run(["docker", "start", "crawl4ai"], check=True)
            return True

        cmd = [
            "docker",
            "run",
            "-d",
            "-p",
            "11235:11235",
            "--name",
            "crawl4ai",
            "--shm-size=1g",
        ]
        crawl_token = api_token or "crawl4ai-token"
        cmd.extend(
            [
                "-e",
                f"CRAWL4AI_API_TOKEN={crawl_token}",
                "-e",
                f"GEMINI_API_TOKEN={crawl_token}",
                "-e",
                f"GEMINI_API_KEY={crawl_token}",
                "-e",
                f"GOOGLE_GENERATIVE_AI_API_KEY={crawl_token}",
            ]
        )
        if model:
            cmd.extend(["-e", f"LLM_PROVIDER={model}"])

        cmd.append("unclecode/crawl4ai:latest")

        logger.info("Deploying Crawl4AI Docker container...")
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(
            "Successfully started Crawl4AI Docker container on http://localhost:11235"
        )
        return True
    except Exception as e:  # noqa: BLE001
        logger.warning(
            f"Failed to start Crawl4AI Docker container: {e}. "
            "Please ensure Docker Desktop is running or start container manually."
        )
        return False


CRAWL4AI_ENTRY = McpRegistryEntry(
    name="crawl4ai",
    description="Crawl4AI open-source LLM-friendly web crawler and scraper MCP server.",
    repository="https://github.com/unclecode/crawl4ai.git",
    package="mcp-crawl4ai-ts",
    default_config=McpStdioServer(
        type="stdio",
        command="npx",
        args=["-y", "mcp-crawl4ai-ts"],
        env={
            "CRAWL4AI_BASE_URL": "http://localhost:11235",
            "CRAWL4AI_API_KEY": "${CRAWL4AI_API_KEY:-crawl4ai-token}",
            "CRAWL4AI_API_TOKEN": "${CRAWL4AI_API_TOKEN:-crawl4ai-token}",
            "GEMINI_API_TOKEN": "${GEMINI_API_TOKEN}",
            "LLM_PROVIDER": "${LLM_PROVIDER:-gemini/gemini-3.5-flash-lite}",
        },
    ),
    init=init_crawl4ai,
)
