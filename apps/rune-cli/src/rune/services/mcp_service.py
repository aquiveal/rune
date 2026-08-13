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
from rune.registry import (
    get_builtin_registry as _get_builtin_registry,
    get_registry as _get_registry,
    search_registry as _search_registry,
)
from rune.registry.mcp.crawl4ai import (
    init_crawl4ai as ensure_crawl4ai_docker_container,
)
from rune.repositories import git_repository, mcp_repository
from rune.schemas.mcp_schema import (
    McpRegistryEntry,
    McpServerUnion,
    McpSettings,
    McpStdioServer,
)
from rune.services import workspace_service
from rune.utils.url import parse_github_url, resolve_url

__all__ = [
    "add_mcp_server",
    "discover_mcp_servers_in_repo",
    "ensure_crawl4ai_docker_container",
    "get_builtin_registry",
    "get_registry",
    "list_mcp_servers",
    "remove_mcp_server",
    "search_registry",
    "validate_mcp_file",
]

logger = structlog.get_logger(__name__)


def _is_tty() -> bool:
    return sys.stdin.isatty()


def get_registry() -> dict[str, McpRegistryEntry]:
    return _get_registry()


def get_builtin_registry() -> dict[str, McpRegistryEntry]:
    return _get_builtin_registry()


def search_registry(query: str) -> list[McpRegistryEntry]:
    return _search_registry(query)


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

    target_agents = workspace_service.resolve_target_agents(
        git_root=git_root,
        cwd=working_dir,
        global_scope=global_scope,
        agents_arg=agent_override,
    )
    if target_agents is None:
        logger.info("MCP server addition cancelled by user.")
        return []

    registry = get_builtin_registry()
    cleaned_source = source.strip().lower()

    if cleaned_source in registry and custom_config is None:
        entry = registry[cleaned_source]
        server_name = entry.name

        probe_api_key = None
        api_token = None
        model = None
        if server_name == "probe":
            for ag in target_agents:
                cfg_path = mcp_repository.get_agent_mcp_config_path(
                    base_dir, ag, global_scope=global_scope
                )
                existing_mcp = mcp_repository.load_mcp_config(cfg_path)
                if server_name in existing_mcp.mcpServers:
                    existing_srv = existing_mcp.mcpServers[server_name]
                    if hasattr(existing_srv, "env") and existing_srv.env:
                        probe_api_key = existing_srv.env.get(
                            "GOOGLE_GENERATIVE_AI_API_KEY"
                        )
                        if probe_api_key:
                            break

            if not probe_api_key:
                probe_api_key = os.environ.get(
                    "GOOGLE_GENERATIVE_AI_API_KEY"
                ) or os.environ.get("GEMINI_API_KEY")

            if not probe_api_key and _is_tty():
                try:
                    prompted = questionary.password(
                        "Enter GOOGLE_GENERATIVE_AI_API_KEY for Probe MCP (press Enter to skip):"
                    ).ask()
                    if prompted:
                        probe_api_key = prompted.strip()
                        os.environ["GOOGLE_GENERATIVE_AI_API_KEY"] = probe_api_key
                except Exception:  # noqa: BLE001, S110
                    pass

        elif server_name == "crawl4ai":
            api_token = None
            model = None
            for ag in target_agents:
                cfg_path = mcp_repository.get_agent_mcp_config_path(
                    base_dir, ag, global_scope=global_scope
                )
                existing_mcp = mcp_repository.load_mcp_config(cfg_path)
                if server_name in existing_mcp.mcpServers:
                    existing_srv = existing_mcp.mcpServers[server_name]
                    if hasattr(existing_srv, "env") and existing_srv.env:
                        api_token = (
                            existing_srv.env.get("GEMINI_API_TOKEN")
                            or existing_srv.env.get("GEMINI_API_KEY")
                            or existing_srv.env.get("GOOGLE_GENERATIVE_AI_API_KEY")
                        )
                        model = existing_srv.env.get(
                            "LLM_PROVIDER"
                        ) or existing_srv.env.get("GEMINI_MODEL")
                        if api_token or model:
                            break

            if not api_token:
                api_token = (
                    os.environ.get("GEMINI_API_TOKEN")
                    or os.environ.get("GEMINI_API_KEY")
                    or os.environ.get("GOOGLE_GENERATIVE_AI_API_KEY")
                )

            if not api_token and _is_tty():
                try:
                    prompted_token = questionary.password(
                        "Enter GEMINI_API_TOKEN / Key for Crawl4AI (press Enter to skip):"
                    ).ask()
                    if prompted_token:
                        api_token = prompted_token.strip()
                        os.environ["GEMINI_API_TOKEN"] = api_token
                except Exception:  # noqa: BLE001, S110
                    pass

            if not model:
                model = os.environ.get("LLM_PROVIDER") or os.environ.get("GEMINI_MODEL")

            if not model and _is_tty():
                try:
                    prompted_model = questionary.text(
                        "Enter Gemini Model for Crawl4AI:",
                        default="gemini/gemini-2.0-flash",
                    ).ask()
                    if prompted_model:
                        model = prompted_model.strip()
                        os.environ["GEMINI_MODEL"] = model
                except Exception:  # noqa: BLE001, S110
                    pass

            if not model:
                model = "gemini/gemini-2.0-flash"

            if entry.init:
                entry.init(api_token=api_token, model=model)

        for agent_key in target_agents:
            norm_key = agent_key.lstrip(".")
            base_cfg = entry.agent_configs.get(norm_key) or entry.default_config
            if not base_cfg:
                continue

            config_path = mcp_repository.get_agent_mcp_config_path(
                base_dir, agent_key, global_scope=global_scope
            )

            cfg = base_cfg.model_copy(deep=True)

            if isinstance(cfg, McpStdioServer):
                if server_name == "probe" and probe_api_key:
                    if not cfg.env:
                        cfg.env = {}
                    cfg.env["GOOGLE_GENERATIVE_AI_API_KEY"] = probe_api_key
                elif server_name == "crawl4ai":
                    if not cfg.env:
                        cfg.env = {}
                    if api_token:
                        cfg.env["GEMINI_API_TOKEN"] = api_token
                        cfg.env["GEMINI_API_KEY"] = api_token
                        cfg.env["GOOGLE_GENERATIVE_AI_API_KEY"] = api_token
                    if model:
                        cfg.env["LLM_PROVIDER"] = model
                        cfg.env["GEMINI_MODEL"] = model

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
