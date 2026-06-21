import pytest
from pathlib import Path
from unittest.mock import patch
from rune.repositories.config_repository import get_repomap_max_tokens

def test_get_repomap_max_tokens_valid_string(tmp_path: Path):
    with patch("rune.repositories.git_repository.get_config", return_value="2048"):
        result = get_repomap_max_tokens(tmp_path)
        assert result == 2048
        assert isinstance(result, int)

def test_get_repomap_max_tokens_none_returns_default(tmp_path: Path):
    with patch("rune.repositories.git_repository.get_config", return_value=None):
        result = get_repomap_max_tokens(tmp_path)
        assert result == 10000

def test_get_repomap_max_tokens_invalid_string_returns_default(tmp_path: Path):
    with patch("rune.repositories.git_repository.get_config", return_value="invalid_value"):
        result = get_repomap_max_tokens(tmp_path)
        assert result == 10000
