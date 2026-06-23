from pathlib import Path
from unittest.mock import patch
from rune.services.map_service import generate_submodule_map


def test_generate_submodule_map_uses_config_default(tmp_path: Path):
    with patch("rune.services.map_service.settings.repomap.max_tokens", 3000):
        with patch("rune.services.map_service.RepoMap") as MockRepoMap:
            MockRepoMap.return_value.get_ranked_tags_map.return_value = "mock_map"

            result = generate_submodule_map(tmp_path)

            assert result == "mock_map"
            # Verify RepoMap was instantiated with map_tokens=3000
            MockRepoMap.assert_called_once()
            _, kwargs = MockRepoMap.call_args
            assert kwargs.get("map_tokens") == 3000


def test_generate_submodule_map_includes_nested_paths_and_excludes_aider_cache(
    tmp_path: Path,
):
    # Setup mock structure
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hello')")

    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_main.py").write_text("def test_hello(): pass")

    # Aider cache
    (tmp_path / ".aider.tags.cache.v4").mkdir()
    (tmp_path / ".aider.tags.cache.v4" / "cache.db").write_text("sqlite3_data")

    # git cache
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("git config")

    with patch("rune.services.map_service.RepoMap") as MockRepoMap:

        def fake_get_ranked_tags_map(chat_fnames, other_fnames):
            return "\n".join(other_fnames)

        MockRepoMap.return_value.get_ranked_tags_map.side_effect = (
            fake_get_ranked_tags_map
        )
        map_text = generate_submodule_map(tmp_path, max_tokens=1000)

    # Assertions
    # Windows uses \ but aider normally normalizes to / or keeps \, so we just check for parts
    assert "src" in map_text
    assert "main.py" in map_text
    assert "tests" in map_text
    assert "test_main.py" in map_text

    # Exclusions
    assert ".aider.tags.cache" not in map_text
    assert "cache.db" not in map_text
    assert ".git" not in map_text
    assert "config" not in map_text
