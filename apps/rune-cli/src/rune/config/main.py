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

    agents: List[str] = [".roo", ".claude", ".cursor", ".cline"]


# Global settings instance
settings = Settings()

# Initialize global logging state
setup_logging(settings)
