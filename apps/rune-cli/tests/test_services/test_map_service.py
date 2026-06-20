import pytest
from pathlib import Path
from rune.services.map_service import generate_submodule_map

def test_generate_submodule_map_includes_nested_paths_and_excludes_aider_cache(tmp_path: Path):
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
