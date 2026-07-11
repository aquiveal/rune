from typing import List, Dict, Tuple, Any, Type
from pathlib import Path
import subprocess

from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
)
from worldline import WorldlineSettings


class RepoMapSettings(BaseModel):
    model: str = "gemini/gemini-3.1-flash-lite"
    max_tokens: int = Field(10000, alias="max-tokens")


class AgentSettings(BaseModel):
    names: List[str] = Field(default_factory=list)


class RuneConfigSource(PydanticBaseSettingsSource):
    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> Tuple[Any, str, bool]:
        return None, field_name, False

    def __call__(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
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
        except Exception:
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

            remotes: Dict[str, str] = {}
            repomap: Dict[str, Any] = {}
            names: List[str] = []

            for line in lines:
                if "=" not in line:
                    continue
                key, val = line.split("=", 1)
                if key == "agent.name":
                    names.append(val)
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
            if remotes:
                d["remotes"] = remotes
            if repomap:
                d["repomap"] = repomap

        except Exception:
            pass

        return d


class Settings(WorldlineSettings, BaseSettings):
    """
    Centralized configuration for Rune.
    Loads values from environment variables and .rune/config with sensible defaults.
    """

    model_config = SettingsConfigDict(extra="ignore")

    # Supported default agents
    agents: List[str] = [".roo", ".claude", ".cursor", ".cline"]

    agent: AgentSettings = Field(default_factory=AgentSettings)
    remotes: Dict[str, str] = Field(default_factory=dict)
    repomap: RepoMapSettings = Field(default_factory=RepoMapSettings)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            RuneConfigSource(settings_cls),
            file_secret_settings,
        )


# Global settings instance
settings = Settings()
