import shutil
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any

import structlog

from rune.config.exceptions import ValidationError
from rune.repositories import mcp_repository, git_repository
from rune.services import workspace_service
from rune.schemas.mcp_schema import (
    McpRegistryEntry,
    McpServerUnion,
    McpSettings,
    McpStdioServer,
)
from rune.utils.url import resolve_url, parse_github_url

logger = structlog.get_logger(__name__)


def get_builtin_registry() -> Dict[str, McpRegistryEntry]:
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

    return {
        "probe": probe_entry,
        "probelabs/probe": probe_entry,
        "filesystem": filesystem_entry,
        "github": github_entry,
        "memory": memory_entry,
    }


def search_registry(query: str) -> List[McpRegistryEntry]:
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


def discover_mcp_servers_in_repo(repo_path: Path) -> Dict[str, McpServerUnion]:
    discovered: Dict[str, McpServerUnion] = {}

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
        except Exception as e:
            logger.warning(f"Could not parse MCP config in {target_file}: {e}")

    return discovered


def add_mcp_server(
    source: str,
    git_root: Optional[Path] = None,
    cwd: Optional[Path] = None,
    global_scope: bool = False,
    agent_override: Optional[List[str]] = None,
    custom_config: Optional[McpServerUnion] = None,
) -> List[Path]:
    working_dir = cwd or Path.cwd()
    base_dir = (Path.home() / ".rune") if global_scope else (git_root or working_dir)
    updated_paths: List[Path] = []

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
            cfg = entry.agent_configs.get(norm_key) or entry.default_config
            if not cfg:
                continue
            config_path = mcp_repository.get_agent_mcp_config_path(
                base_dir, agent_key, global_scope=global_scope
            )
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
) -> Dict[str, Dict[str, Any]]:
    agent_paths = mcp_repository.get_all_agent_mcp_config_paths(
        base_dir, global_scope=global_scope
    )
    result: Dict[str, Dict[str, Any]] = {}

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
        except Exception:
            pass

    return result


def remove_mcp_server(
    names: List[str], base_dir: Path, global_scope: bool = False
) -> List[Path]:
    agent_paths = mcp_repository.get_all_agent_mcp_config_paths(
        base_dir, global_scope=global_scope
    )
    modified_paths: List[Path] = []

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
