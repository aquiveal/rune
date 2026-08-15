import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)
from python_logging.config import LoggingSettings

__all__ = [
    "Agent",
    "AgentPaths",
    "AgentSettings",
    "RepoMapSettings",
    "RuneConfigSource",
    "Settings",
    "get_default_agents",
    "settings",
]


class RepoMapSettings(BaseModel):
    model: str = "gemini/gemini-3.1-flash-lite"
    max_tokens: int = Field(10000, alias="max-tokens")


class AgentSettings(BaseModel):
    names: list[str] = Field(default_factory=list)


class AgentPaths(BaseModel):
    rules: str
    skills: str
    mcp: str


class Agent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    workspace: AgentPaths
    global_scope: AgentPaths = Field(alias="global")


def get_default_agents() -> dict[str, Agent]:
    try:
        home = Path.home()
    except Exception:  # noqa: BLE001
        home = Path("~")

    app_data = (
        os.environ.get("APPDATA", str(home / "AppData" / "Roaming"))
        if sys.platform == "win32"
        else ""
    )

    if sys.platform == "win32":
        roo_mcp_global = str(Path(app_data) / "Roo-Code" / "MCP" / "mcp-settings.json")
    elif sys.platform == "darwin":
        roo_mcp_global = str(
            home / ".local" / "share" / "Roo-Code" / "MCP" / "mcp-settings.json"
        )
    else:
        roo_mcp_global = str(
            home / ".local" / "share" / "Roo-Code" / "MCP" / "mcp-settings.json"
        )

    if sys.platform == "darwin":
        cline_mcp_global = str(
            home / "Documents" / "Cline" / "MCP" / "mcp-settings.json"
        )
    elif sys.platform == "win32":
        cline_mcp_global = str(Path(app_data) / "Cline" / "MCP" / "mcp-settings.json")
    else:
        cline_mcp_global = str(
            home / ".local" / "share" / "Cline" / "MCP" / "mcp-settings.json"
        )

    return {
        ".agents": Agent(
            workspace=AgentPaths(
                rules=".agents/rules", skills=".agents/skills", mcp=".agents/mcp.json"
            ),
            global_scope=AgentPaths(
                rules=".agents/rules",
                skills=".agents/skills",
                mcp=str(home / ".rune" / "mcp.json"),
            ),
        ),
        ".roo": Agent(
            workspace=AgentPaths(
                rules=".roo/rules", skills=".roo/skills", mcp=".roo/mcp.json"
            ),
            global_scope=AgentPaths(
                rules=".roo/rules", skills=".roo/skills", mcp=roo_mcp_global
            ),
        ),
        ".claude": Agent(
            workspace=AgentPaths(
                rules=".claude/rules", skills=".claude/skills", mcp=".claude/mcp.json"
            ),
            global_scope=AgentPaths(
                rules=".claude/rules",
                skills=".claude/skills",
                mcp=str(home / ".claude" / "claude_desktop_config.json"),
            ),
        ),
        ".cursor": Agent(
            workspace=AgentPaths(
                rules=".cursor/rules", skills=".cursor/skills", mcp=".cursor/mcp.json"
            ),
            global_scope=AgentPaths(
                rules=".cursor/rules",
                skills=".cursor/skills",
                mcp=str(home / ".cursor" / "mcp.json"),
            ),
        ),
        ".cline": Agent(
            workspace=AgentPaths(
                rules=".cline/rules", skills=".cline/skills", mcp=".cline/mcp.json"
            ),
            global_scope=AgentPaths(
                rules=".cline/rules", skills=".cline/skills", mcp=cline_mcp_global
            ),
        ),
    }


class RuneConfigSource(PydanticBaseSettingsSource):
    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> tuple[Any, str, bool]:
        return None, field_name, False

    def __call__(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        cwd = Path.cwd()
        root_dir = cwd
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                check=True,
            )
            root_dir = Path(result.stdout.strip())
        except Exception:  # noqa: BLE001, S110
            pass

        config_path = root_dir / ".rune" / "config"
        if not config_path.exists():
            return d

        try:
            result = subprocess.run(
                ["git", "config", "--file", str(config_path), "-l"],
                capture_output=True,
                text=True,
                check=True,
            )
            lines = result.stdout.splitlines()

            remotes: dict[str, str] = {}
            repomap: dict[str, Any] = {}
            names: list[str] = []
            submodules: list[str] = []

            for line in lines:
                if "=" not in line:
                    continue
                key, val = line.split("=", 1)
                if key == "agent.name":
                    names.append(val)
                elif key == "submodule.path":
                    submodules.append(val)
                elif key.startswith("remote.") and key.endswith(".url"):
                    alias = key.split(".")[1]
                    remotes[alias] = val
                elif key.startswith("repomap."):
                    sub_key = key.split(".", 1)[1]
                    if sub_key == "max-tokens":
                        try:
                            val = int(val)  # type: ignore
                        except ValueError:
                            pass
                    repomap[sub_key] = val

            if names:
                d["agent"] = {"names": names}
            if submodules:
                d["submodules"] = submodules
            if remotes:
                d["remotes"] = remotes
            if repomap:
                d["repomap"] = repomap

        except Exception:  # noqa: BLE001, S110
            pass

        return d


class Settings(LoggingSettings, BaseSettings):
    """
    Centralized configuration for Rune.
    Loads values from environment variables and .rune/config with sensible defaults.
    """

    model_config = SettingsConfigDict(extra="ignore")

    agent: AgentSettings = Field(default_factory=AgentSettings)
    agent_paths: dict[str, Agent] = Field(default_factory=get_default_agents)
    submodules: list[str] = Field(default_factory=list)
    remotes: dict[str, str] = Field(default_factory=dict)
    repomap: RepoMapSettings = Field(default_factory=RepoMapSettings)

    def get_submodule_paths(self, root_dir: Path) -> list[Path]:
        """Return list of existing relative submodule directory paths explicitly configured in submodule.path."""
        paths: list[Path] = []
        for sub in self.submodules:
            clean_sub = sub.strip().replace("\\", "/")
            if not clean_sub:
                continue
            sub_path = root_dir / Path(clean_sub)
            if sub_path.exists() and sub_path.is_dir() and sub_path not in paths:
                paths.append(sub_path)
        return paths

    @property
    def agents(self) -> list[str]:
        """Return list of supported default agent directory names (e.g. ['.roo', '.claude', ...])."""
        return [k for k in self.agent_paths if k != ".agents"]

    def get_agent(self, name: str) -> Agent | None:
        """Lookup an Agent object by name (accepts with or without leading dot)."""
        key = name if name.startswith(".") else f".{name}"
        if key in self.agent_paths:
            return self.agent_paths[key]
        if name in self.agent_paths:
            return self.agent_paths[name]
        return None

    def get_skill_search_paths(self) -> list[str]:
        """Return deduplicated relative skill search directory paths including configured submodules."""
        paths = ["skills"]
        for agent_cfg in self.agent_paths.values():
            skills_path = agent_cfg.workspace.skills
            if skills_path and skills_path not in paths:
                paths.append(skills_path)
        for sub in self.submodules:
            clean_sub = sub.strip().replace("\\", "/")
            if not clean_sub:
                continue
            for agent_cfg in self.agent_paths.values():
                sub_skills = f"{clean_sub}/{agent_cfg.workspace.skills}"
                if sub_skills not in paths:
                    paths.append(sub_skills)
            sub_default_skills = f"{clean_sub}/skills"
            if sub_default_skills not in paths:
                paths.append(sub_default_skills)
        return paths

    def get_rule_search_paths(self) -> list[str]:
        """Return deduplicated relative rule search directory paths including configured submodules."""
        paths = ["rules"]
        for agent_cfg in self.agent_paths.values():
            rules_path = agent_cfg.workspace.rules
            if rules_path and rules_path not in paths:
                paths.append(rules_path)
        for sub in self.submodules:
            clean_sub = sub.strip().replace("\\", "/")
            if not clean_sub:
                continue
            for agent_cfg in self.agent_paths.values():
                sub_rules = f"{clean_sub}/{agent_cfg.workspace.rules}"
                if sub_rules not in paths:
                    paths.append(sub_rules)
            sub_default_rules = f"{clean_sub}/rules"
            if sub_default_rules not in paths:
                paths.append(sub_default_rules)
        return paths

    def get_mcp_search_paths(self, global_scope: bool = False) -> dict[str, str]:
        """Return mapping of agent key to MCP config file path."""
        result = {}
        for agent_key, agent_cfg in self.agent_paths.items():
            normalized_key = agent_key.lstrip(".")
            if global_scope:
                result[normalized_key] = agent_cfg.global_scope.mcp
            else:
                result[normalized_key] = agent_cfg.workspace.mcp
        return result

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            RuneConfigSource(settings_cls),
            file_secret_settings,
        )


# Global settings instance
settings = Settings()
