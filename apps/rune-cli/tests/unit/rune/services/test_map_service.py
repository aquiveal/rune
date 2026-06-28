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


def test_generate_submodule_map_honors_gitignore(tmp_path: Path):
    # Setup mock structure
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hello')")
    
    (tmp_path / "ignored_dir").mkdir()
    (tmp_path / "ignored_dir" / "secret.txt").write_text("shhh")
    (tmp_path / "ignored_file.txt").write_text("ignore me")
    
    # Create .gitignore
    (tmp_path / ".gitignore").write_text("ignored_dir/\nignored_file.txt")

    with patch("rune.services.map_service.RepoMap") as MockRepoMap:
        def fake_get_ranked_tags_map(chat_fnames, other_fnames):
            return "\n".join(other_fnames)

        MockRepoMap.return_value.get_ranked_tags_map.side_effect = fake_get_ranked_tags_map
        map_text = generate_submodule_map(tmp_path, max_tokens=1000)

    # Assertions
    assert "src" in map_text
    assert "main.py" in map_text
    
    # Exclusions via .gitignore
    assert "ignored_dir" not in map_text
    assert "secret.txt" not in map_text
    assert "ignored_file.txt" not in map_text


def test_generate_submodule_map_honors_gitignore_with_complex_patterns(tmp_path: Path):
    # Setup mock structure
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hello')")
    
    (tmp_path / ".rune").mkdir()
    (tmp_path / ".rune" / "config").write_text("key=value")
    
    (tmp_path / ".rune" / "modules").mkdir()
    (tmp_path / ".rune" / "modules" / "test.py").write_text("test")
    
    # Create .gitignore with complex patterns
    (tmp_path / ".gitignore").write_text(".rune/*\n!.rune/config\n")

    with patch("rune.services.map_service.RepoMap") as MockRepoMap:
        def fake_get_ranked_tags_map(chat_fnames, other_fnames):
            return "\n".join(other_fnames)

        MockRepoMap.return_value.get_ranked_tags_map.side_effect = fake_get_ranked_tags_map
        map_text = generate_submodule_map(tmp_path, max_tokens=1000)

    # Assertions
    assert "src" in map_text
    assert "main.py" in map_text
    
    # Assert negation logic (.rune/config should be included)
    assert "config" in map_text
    
    # Assert wildcard exclusion (.rune/modules/test.py should be excluded)
    assert "test.py" not in map_text


def test_merge_ast_to_agents_md_creates_new(tmp_path: Path):
    from rune.services.map_service import merge_ast_to_agents_md

    ast_content = "def hello():\n    pass"
    merge_ast_to_agents_md(tmp_path, ast_content)

    agents_md = tmp_path / "AGENTS.md"
    assert agents_md.exists()
    content = agents_md.read_text(encoding="utf-8")
    assert "# Repository Map" in content
    assert "def hello():" in content


def test_merge_ast_to_agents_md_appends_to_existing(tmp_path: Path):
    from rune.services.map_service import merge_ast_to_agents_md

    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text("# Existing Content\n\nSome rules.", encoding="utf-8")

    ast_content = "class Mock:"
    merge_ast_to_agents_md(tmp_path, ast_content)

    content = agents_md.read_text(encoding="utf-8")
    assert content.startswith("# Existing Content")
    assert "# Repository Map" in content
    assert "class Mock:" in content


def test_merge_ast_to_agents_md_replaces_existing(tmp_path: Path):
    from rune.services.map_service import merge_ast_to_agents_md

    agents_md = tmp_path / "AGENTS.md"
    initial_content = "# Rules\n\n- Rule 1\n\n# Repository Map\n\n```python\nold_ast()\n```\n"
    agents_md.write_text(initial_content, encoding="utf-8")

    ast_content = "new_ast()"
    merge_ast_to_agents_md(tmp_path, ast_content)

    content = agents_md.read_text(encoding="utf-8")
    assert "# Rules\n\n- Rule 1\n\n" in content
    assert "old_ast()" not in content
    assert "new_ast()" in content
    assert "# Repository Map" in content
