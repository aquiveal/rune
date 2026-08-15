import re
from typing import Any, ClassVar

from rune.config.exceptions import ValidationError

__all__ = ["ConfigKeyValidator", "validate_config_key_value"]


class ConfigKeyValidator:
    ALLOWED_KEYS: ClassVar[dict[str, str]] = {
        "agent.name": r"^.+$",
        "submodule.path": r"^(?!\/)(?!.*(?:\.\.|\/\.\.))[a-zA-Z0-9_\-\./]+$",
        "repomap.model": r"^[a-zA-Z0-9_\-\./]+$",
        "repomap.max-tokens": r"^\d+$",
    }

    PREFIX_PATTERNS: ClassVar[dict[str, str]] = {
        "remote.": r"^remote\.[a-zA-Z0-9_\-]+\.url$",
    }

    @classmethod
    def is_valid_key(cls, key: str) -> bool:
        if key in cls.ALLOWED_KEYS:
            return True
        for prefix, pattern in cls.PREFIX_PATTERNS.items():
            if key.startswith(prefix) and re.match(pattern, key):
                return True
        return False

    @classmethod
    def validate_value(cls, key: str, value: str | None) -> bool:
        if value is None:
            return True

        if key in cls.ALLOWED_KEYS:
            pattern = cls.ALLOWED_KEYS[key]
            return bool(re.match(pattern, value))

        for prefix in cls.PREFIX_PATTERNS:
            if key.startswith(prefix):
                return bool(value.strip())

        return False


def validate_config_key_value(key: str, value: str | None = None) -> Any:
    if not ConfigKeyValidator.is_valid_key(key):
        raise ValidationError(
            f"Invalid or unsupported configuration key '{key}'. "
            "Supported keys include: agent.name, submodule.path, remote.<alias>.url, repomap.model, repomap.max-tokens"
        )

    if value is not None and not ConfigKeyValidator.validate_value(key, value):
        raise ValidationError(f"Invalid value '{value}' for configuration key '{key}'")

    if key == "repomap.max-tokens" and value is not None:
        return int(value)

    return value
