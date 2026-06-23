from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from python_logging.config import LoggingSettings
from python_logging.main import setup_logging


class Settings(LoggingSettings, BaseSettings):
    """
    Centralized configuration for Rune.
    Loads values from environment variables with sensible defaults.
    """

    model_config = SettingsConfigDict(extra="ignore")

    rune_dir: str = ".rune"
    rune_config: str = "config"
    rune_modules_file: str = ".runemodules"
    rune_modules_dir: str = "modules"
    rune_tmp_dir: str = "tmp"
    rune_index: str = "index"
    default_agents: List[str] = [".roo", ".claude", ".cursor", ".cline"]

    @property
    def global_rune_dir(self) -> Path:
        return Path.home() / self.rune_dir


# Global settings instance
settings = Settings()

# Initialize global logging state
setup_logging(settings)
