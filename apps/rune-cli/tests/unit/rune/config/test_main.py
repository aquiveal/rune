import os
from unittest import mock


def test_settings_initialization_with_extra_kwargs():
    from rune.config.main import Settings

    with mock.patch.dict(os.environ, {"RANDOM_UNKNOWN_VAR": "test"}, clear=True):
        settings = Settings()
        assert settings.model_config.get("extra") == "ignore"


def test_settings_setup_logging_is_called():
    with mock.patch("python_logging.main.setup_logging") as mock_setup_logging:
        import importlib
        import rune.config.main

        # Reloading to trigger module level initialization
        importlib.reload(rune.config.main)

        mock_setup_logging.assert_called_once_with(rune.config.main.settings)
