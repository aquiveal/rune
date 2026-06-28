import os
from unittest import mock


def test_settings_initialization_with_extra_kwargs():
    from rune.config.main import Settings

    with mock.patch.dict(os.environ, {"RANDOM_UNKNOWN_VAR": "test"}, clear=True):
        settings = Settings()
        assert settings.model_config.get("extra") == "ignore"
