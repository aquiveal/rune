import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

import questionary
import structlog

from rune.config.exceptions import ValidationError
from rune.repositories import git_repository, mcp_repository
from rune.schemas.mcp_schema import (
    McpRegistryEntry,
    McpServerUnion,
    McpSettings,
    McpSseServer,
    McpStdioServer,
)
from rune.services import workspace_service
from rune.utils.url import parse_github_url, resolve_url

__all__ = [
    "add_mcp_server",
    "discover_mcp_servers_in_repo",
    "get_builtin_registry",
    "list_mcp_servers",
    "remove_mcp_server",
    "search_registry",
    "validate_mcp_file",
]

logger = structlog.get_logger(__name__)


def get_builtin_registry() -> dict[str, McpRegistryEntry]:
    probe_entry = McpRegistryEntry(
        name="probe",
        description="Probe is a code and markdown context engine with a built-in agent, made to work on enterprise-scale codebases.",
        repository="https://github.com/probelabs/probe.git",
        package="@probelabs/probe",
        agent_configs={
            "roo": McpStdioServer(
                type="stdio",
                command="npx",
                args=["-y", "@probelabs/probe@latest", "agent", "--mcp"],
            ),
            "cline": McpStdioServer(
                type="stdio",
                command="npx",
                args=["-y", "@probelabs/probe@latest", "agent", "--mcp"],
            ),
            "claude": McpStdioServer(
                type="stdio",
                command="npx",
                args=["-y", "@probelabs/probe@latest", "agent", "--mcp"],
            ),
            "cursor": McpStdioServer(
                type="stdio",
                command="npx",
                args=["-y", "@probelabs/probe@latest", "mcp"],
            ),
            "agents": McpStdioServer(
                type="stdio",
                command="npx",
                args=["-y", "@probelabs/probe@latest", "agent", "--mcp"],
            ),
        },
        default_config=McpStdioServer(
            type="stdio",
            command="npx",
            args=["-y", "@probelabs/probe@latest", "agent", "--mcp"],
        ),
    )

    filesystem_entry = McpRegistryEntry(
        name="filesystem",
        description="File system access MCP server for reading and modifying local files.",
        repository="https://github.com/modelcontextprotocol/servers.git",
        package="@modelcontextprotocol/server-filesystem",
        default_config=McpStdioServer(
            type="stdio",
            command="npx",
            args=[
                "-y",
                "@modelcontextprotocol/server-filesystem",
                "${workspaceFolder}",
            ],
        ),
    )

    github_entry = McpRegistryEntry(
        name="github",
        description="GitHub MCP server for searching repos, issues, pull requests, and code.",
        repository="https://github.com/modelcontextprotocol/servers.git",
        package="@modelcontextprotocol/server-github",
        default_config=McpStdioServer(
            type="stdio",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-github"],
            env={"GITHUB_PERSONAL_ACCESS_TOKEN": ""},
        ),
    )

    memory_entry = McpRegistryEntry(
        name="memory",
        description="Knowledge graph persistent memory MCP server.",
        repository="https://github.com/modelcontextprotocol/servers.git",
        package="@modelcontextprotocol/server-memory",
        default_config=McpStdioServer(
            type="stdio",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-memory"],
        ),
    )

    crawl4ai_entry = McpRegistryEntry(
        name="crawl4ai",
        description="Crawl4AI open-source LLM-friendly web crawler and scraper MCP server.",
        repository="https://github.com/unclecode/crawl4ai.git",
        package="crawl4ai",
        default_config=McpSseServer(
            type="sse",
            url="http://localhost:11235/mcp/sse",
        ),
    )

    return {
        "probe": probe_entry,
        "probelabs/probe": probe_entry,
        "filesystem": filesystem_entry,
        "github": github_entry,
        "memory": memory_entry,
        "crawl4ai": crawl4ai_entry,
        "unclecode/crawl4ai": crawl4ai_entry,
    }


def ensure_crawl4ai_docker_container(
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
        if api_token:
            cmd.extend(
                [
                    "-e",
                    f"GEMINI_API_TOKEN={api_token}",
                    "-e",
                    f"GEMINI_API_KEY={api_token}",
                    "-e",
                    f"GOOGLE_GENERATIVE_AI_API_KEY={api_token}",
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


def search_registry(query: str) -> list[McpRegistryEntry]:
    q = query.lower().strip()
    registry = get_builtin_registry()
    seen = set()
    results = []
    for entry in registry.values():
        if entry.name in seen:
            continue
        if (
            q in entry.name.lower()
            or q in entry.description.lower()
            or (entry.package and q in entry.package.lower())
        ):
            seen.add(entry.name)
            results.append(entry)
    return results


def discover_mcp_servers_in_repo(repo_path: Path) -> dict[str, McpServerUnion]:
    discovered: dict[str, McpServerUnion] = {}

    mcp_json = repo_path / "mcp.json"
    mcp_servers_json = repo_path / "mcp-servers.json"

    target_file = None
    if mcp_json.exists():
        target_file = mcp_json
    elif mcp_servers_json.exists():
        target_file = mcp_servers_json

    if target_file:
        try:
            settings = mcp_repository.load_mcp_config(target_file)
            discovered.update(settings.mcpServers)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Could not parse MCP config in {target_file}: {e}")

    return discovered


def add_mcp_server(
    source: str,
    git_root: Path | None = None,
    cwd: Path | None = None,
    global_scope: bool = False,
    agent_override: list[str] | None = None,
    custom_config: McpServerUnion | None = None,
) -> list[Path]:
    working_dir = cwd or Path.cwd()
    base_dir = (Path.home() / ".rune") if global_scope else (git_root or working_dir)
    updated_paths: list[Path] = []

    target_agents = (
        workspace_service.resolve_target_agents(
            git_root=git_root,
            cwd=working_dir,
            global_scope=global_scope,
            agents_arg=agent_override,
        )
        or []
    )

    registry = get_builtin_registry()
    cleaned_source = source.strip().lower()

    if cleaned_source in registry and custom_config is None:
        entry = registry[cleaned_source]
        server_name = entry.name

        for agent_key in target_agents:
            norm_key = agent_key.lstrip(".")
            base_cfg = entry.agent_configs.get(norm_key) or entry.default_config
            if not base_cfg:
                continue

            config_path = mcp_repository.get_agent_mcp_config_path(
                base_dir, agent_key, global_scope=global_scope
            )

            cfg = base_cfg.model_copy(deep=True)

            if server_name == "probe":
                existing_mcp = mcp_repository.load_mcp_config(config_path)
                existing_key = None
                if server_name in existing_mcp.mcpServers:
                    existing_server = existing_mcp.mcpServers[server_name]
                    if hasattr(existing_server, "env") and existing_server.env:
                        existing_key = existing_server.env.get(
                            "GOOGLE_GENERATIVE_AI_API_KEY"
                        )

                api_key = (
                    existing_key
                    or os.environ.get("GOOGLE_GENERATIVE_AI_API_KEY")
                    or os.environ.get("GEMINI_API_KEY")
                )

                if not api_key and sys.stdin.isatty():
                    try:
                        prompted = questionary.password(
                            "Enter GOOGLE_GENERATIVE_AI_API_KEY for Probe MCP (press Enter to skip):"
                        ).ask()
                        if prompted:
                            api_key = prompted.strip()
                    except Exception:  # noqa: BLE001, S110
                        pass

                if api_key and isinstance(cfg, McpStdioServer):
                    if not cfg.env:
                        cfg.env = {}
                    cfg.env["GOOGLE_GENERATIVE_AI_API_KEY"] = api_key

            elif server_name == "crawl4ai":
                api_token = (
                    os.environ.get("GEMINI_API_TOKEN")
                    or os.environ.get("GEMINI_API_KEY")
                    or os.environ.get("GOOGLE_GENERATIVE_AI_API_KEY")
                )

                if not api_token and sys.stdin.isatty():
                    try:
                        prompted_token = questionary.password(
                            "Enter GEMINI_API_TOKEN / Key for Crawl4AI (press Enter to skip):"
                        ).ask()
                        if prompted_token:
                            api_token = prompted_token.strip()
                    except Exception:  # noqa: BLE001, S110
                        pass

                model = os.environ.get("LLM_PROVIDER") or os.environ.get("GEMINI_MODEL")
                if not model and sys.stdin.isatty():
                    try:
                        prompted_model = questionary.text(
                            "Enter Gemini Model for Crawl4AI:",
                            default="gemini/gemini-2.0-flash",
                        ).ask()
                        if prompted_model:
                            model = prompted_model.strip()
                    except Exception:  # noqa: BLE001, S110
                        pass

                if not model:
                    model = "gemini/gemini-2.0-flash"

                ensure_crawl4ai_docker_container(api_token=api_token, model=model)

            mcp_repository.add_server_config(config_path, server_name, cfg)
            updated_paths.append(config_path)

        return updated_paths

    if custom_config is not None:
        for ag in target_agents:
            config_path = mcp_repository.get_agent_mcp_config_path(
                base_dir, ag, global_scope=global_scope
            )
            mcp_repository.add_server_config(config_path, source, custom_config)
            updated_paths.append(config_path)
        return updated_paths

    # Check local JSON file
    local_path = Path(source)
    if not local_path.is_absolute():
        local_path = working_dir / local_path

    if local_path.exists() and local_path.is_file() and local_path.suffix == ".json":
        settings = mcp_repository.load_mcp_config(local_path)
        if not settings.mcpServers:
            raise ValidationError(f"No mcpServers defined in '{local_path}'.")

        for name, s_cfg in settings.mcpServers.items():
            for ag in target_agents:
                config_path = mcp_repository.get_agent_mcp_config_path(
                    base_dir, ag, global_scope=global_scope
                )
                mcp_repository.add_server_config(config_path, name, s_cfg)
                updated_paths.append(config_path)
        return updated_paths

    # Otherwise treat as Git URL or shorthand owner/repo
    raw_url = resolve_url(source, git_root or working_dir)
    url, extracted_path = parse_github_url(raw_url)

    tmp_dir = (git_root or working_dir) / ".rune" / "tmp" / str(uuid.uuid4())
    tmp_dir.mkdir(parents=True, exist_ok=True)

    try:
        git_repository.clone(url, tmp_dir, depth=1)
        search_path = tmp_dir / extracted_path if extracted_path else tmp_dir
        discovered = discover_mcp_servers_in_repo(search_path)

        if not discovered:
            # Fallback: scaffold stdio server from repo name
            repo_name = url.rstrip("/").split("/")[-1].replace(".git", "")
            discovered = {
                repo_name: McpStdioServer(
                    type="stdio",
                    command="node",
                    args=["index.js"],
                    cwd=str(search_path),
                )
            }

        for s_name, s_cfg in discovered.items():
            for ag in target_agents:
                config_path = mcp_repository.get_agent_mcp_config_path(
                    base_dir, ag, global_scope=global_scope
                )
                mcp_repository.add_server_config(config_path, s_name, s_cfg)
                updated_paths.append(config_path)

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    return updated_paths


def list_mcp_servers(
    base_dir: Path, global_scope: bool = False
) -> dict[str, dict[str, Any]]:
    agent_paths = mcp_repository.get_all_agent_mcp_config_paths(
        base_dir, global_scope=global_scope
    )
    result: dict[str, dict[str, Any]] = {}

    for agent_key, cfg_path in agent_paths.items():
        if not cfg_path.exists():
            continue
        try:
            settings = mcp_repository.load_mcp_config(cfg_path)
            for s_name, s_cfg in settings.mcpServers.items():
                if s_name not in result:
                    result[s_name] = {
                        "config": s_cfg.model_dump(exclude_none=True),
                        "agents": [agent_key],
                        "paths": [str(cfg_path)],
                    }
                else:
                    result[s_name]["agents"].append(agent_key)
                    result[s_name]["paths"].append(str(cfg_path))
        except Exception:  # noqa: BLE001, S110
            pass

    return result


def remove_mcp_server(
    names: list[str], base_dir: Path, global_scope: bool = False
) -> list[Path]:
    agent_paths = mcp_repository.get_all_agent_mcp_config_paths(
        base_dir, global_scope=global_scope
    )
    modified_paths: list[Path] = []

    for name in names:
        for cfg_path in agent_paths.values():
            if cfg_path.exists():
                removed = mcp_repository.remove_server_config(cfg_path, name)
                if removed and cfg_path not in modified_paths:
                    modified_paths.append(cfg_path)

    return modified_paths


def validate_mcp_file(path: Path) -> McpSettings:
    if not path.exists():
        raise ValidationError(f"Configuration file '{path}' does not exist.")
    return mcp_repository.load_mcp_config(path)
