import pytest
from rune.config.exceptions import ValidationError
from rune.schemas.config_schema import validate_config_key_value


def test_valid_agent_name():
    assert validate_config_key_value("agent.name", ".roo") == ".roo"
    assert validate_config_key_value("agent.name", ".claude") == ".claude"


def test_invalid_agent_name():
    with pytest.raises(ValidationError):
        validate_config_key_value("agent.name", "")


def test_valid_remote_url():
    assert (
        validate_config_key_value("remote.origin.url", "https://github.com/foo/bar.git")
        == "https://github.com/foo/bar.git"
    )


def test_invalid_remote_url():
    with pytest.raises(ValidationError):
        validate_config_key_value(
            "remote.invalid..url", "https://github.com/foo/bar.git"
        )


def test_valid_repomap_settings():
    assert validate_config_key_value("repomap.model", "gemini/flash") == "gemini/flash"
    assert validate_config_key_value("repomap.max-tokens", "10000") == 10000


def test_invalid_repomap_max_tokens():
    with pytest.raises(ValidationError):
        validate_config_key_value("repomap.max-tokens", "-50")
    with pytest.raises(ValidationError):
        validate_config_key_value("repomap.max-tokens", "not-a-number")


def test_valid_submodule_path():
    assert (
        validate_config_key_value("submodule.path", "submodules/frontend")
        == "submodules/frontend"
    )


def test_invalid_submodule_path():
    with pytest.raises(ValidationError):
        validate_config_key_value("submodule.path", "../outside")
    with pytest.raises(ValidationError):
        validate_config_key_value("submodule.path", "/absolute/path")


def test_unknown_key():
    with pytest.raises(ValidationError):
        validate_config_key_value("unknown.invalid.key", "value")
