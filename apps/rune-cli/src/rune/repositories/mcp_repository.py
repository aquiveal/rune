import json
import os
import sys
from pathlib import Path

from rune.config.exceptions import ConfigError
from rune.config.main import settings
from rune.schemas.mcp_schema import McpServerUnion, McpSettings

__all__ = [
    "add_server_config",
    "get_agent_mcp_config_path",
    "get_all_agent_mcp_config_paths",
    "load_mcp_config",
    "remove_server_config",
    "save_mcp_config",
]


def _normalize_agent_name(agent: str) -> str:
    cleaned = agent.lstrip(".")
    if cleaned in ("roo", "roo-code", "zoo", "zoo-code"):
        return "roo"
    if cleaned == "cline":
        return "cline"
    if cleaned in ("claude", "claude-desktop"):
        return "claude"
    if cleaned == "cursor":
        return "cursor"
    return "agents"


def get_agent_mcp_config_path(
    base_dir: Path, agent: str, global_scope: bool = False
) -> Path:
    agent_key = _normalize_agent_name(agent)
    home = Path.home()

    # Special check for Zoo Code global path if roo agent is targeted
    if global_scope and agent_key == "roo":
        if sys.platform == "win32":
            app_data = os.environ.get("APPDATA", str(home / "AppData" / "Roaming"))
            zoo_path = (
                Path(app_data)
                / "Code"
                / "User"
                / "globalStorage"
                / "zoocodeorganization.zoo-code"
                / "settings"
                / "mcp_settings.json"
            )
            if zoo_path.parent.exists() or zoo_path.exists():
                return zoo_path
        elif sys.platform == "darwin":
            zoo_path = (
                home
                / "Library"
                / "Application Support"
                / "Code"
                / "User"
                / "globalStorage"
                / "zoocodeorganization.zoo-code"
                / "settings"
                / "mcp_settings.json"
            )
            if zoo_path.parent.exists() or zoo_path.exists():
                return zoo_path
        else:
            zoo_path = (
                home
                / ".config"
                / "Code"
                / "User"
                / "globalStorage"
                / "zoocodeorganization.zoo-code"
                / "settings"
                / "mcp_settings.json"
            )
            if zoo_path.parent.exists() or zoo_path.exists():
                return zoo_path

    agent_obj = settings.get_agent(agent_key)
    if agent_obj:
        if global_scope:
            return Path(agent_obj.global_scope.mcp)
        else:
            return base_dir / Path(agent_obj.workspace.mcp)

    agent_dir_name = f".{agent_key}" if agent_key != "agents" else ".agents"
    return base_dir / agent_dir_name / "mcp.json"


def get_all_agent_mcp_config_paths(
    base_dir: Path, global_scope: bool = False
) -> dict[str, Path]:
    mcp_map = settings.get_mcp_search_paths(global_scope=global_scope)
    paths = {}
    for agent_key in mcp_map:
        paths[agent_key] = get_agent_mcp_config_path(base_dir, agent_key, global_scope)

    # If in global scope, also explicitly include Zoo Code path if distinct from Roo Code path
    if global_scope:
        home = Path.home()
        if sys.platform == "win32":
            app_data = os.environ.get("APPDATA", str(home / "AppData" / "Roaming"))
            zoo_path = (
                Path(app_data)
                / "Code"
                / "User"
                / "globalStorage"
                / "zoocodeorganization.zoo-code"
                / "settings"
                / "mcp_settings.json"
            )
            if zoo_path.parent.exists() or zoo_path.exists():
                paths["zoo"] = zoo_path
    return paths


def load_mcp_config(config_path: Path) -> McpSettings:
    if not config_path.exists():
        return McpSettings()

    try:
        content = config_path.read_text(encoding="utf-8")
        if not content.strip():
            return McpSettings()
        data = json.loads(content)
        return McpSettings.model_validate(data)
    except json.JSONDecodeError as e:
        raise ConfigError(
            f"Invalid JSON in MCP configuration file '{config_path}': {e}"
        )
    except Exception as e:  # noqa: BLE001
        raise ConfigError(f"Failed to load MCP configuration from '{config_path}': {e}")


def save_mcp_config(config_path: Path, settings: McpSettings) -> None:
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        dump_data = settings.model_dump(exclude_none=True, mode="json")
        json_str = json.dumps(dump_data, indent=2)
        config_path.write_text(json_str, encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        raise ConfigError(f"Failed to save MCP configuration to '{config_path}': {e}")


def add_server_config(
    config_path: Path, name: str, server_config: McpServerUnion
) -> None:
    settings = load_mcp_config(config_path)
    settings.mcpServers[name] = server_config
    save_mcp_config(config_path, settings)


def remove_server_config(config_path: Path, name: str) -> bool:
    settings = load_mcp_config(config_path)
    if name in settings.mcpServers:
        del settings.mcpServers[name]
        save_mcp_config(config_path, settings)
        return True
    return False
