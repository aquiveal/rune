from pathlib import Path
from rune.services.map_service import generate_submodule_map, merge_ast_to_agents_md


def test_generate_submodule_map(tmp_path: Path):
    result = generate_submodule_map(tmp_path)
    assert "Directory:" in result
    assert "probe search" in result


def test_merge_ast_to_agents_md_creates_new(tmp_path: Path):
    merge_ast_to_agents_md(tmp_path, "ast_content")

    agents_md = tmp_path / "AGENTS.md"
    assert agents_md.exists()
    content = agents_md.read_text(encoding="utf-8")
    assert "# Code Context Engine (Probe)" in content
    assert "probe search" in content
    assert "```python" not in content  # No raw AST dump


def test_merge_ast_to_agents_md_replaces_old_repo_map(tmp_path: Path):
    agents_md = tmp_path / "AGENTS.md"
    initial_content = (
        "# Rules\n\n- Rule 1\n\n# Repository Map\n\n```python\nold_ast()\n```\n"
    )
    agents_md.write_text(initial_content, encoding="utf-8")

    merge_ast_to_agents_md(tmp_path, "new_ast()")

    content = agents_md.read_text(encoding="utf-8")
    assert "# Rules\n\n- Rule 1\n\n" in content
    assert "old_ast()" not in content
    assert "```python" not in content
    assert "# Code Context Engine (Probe)" in content
