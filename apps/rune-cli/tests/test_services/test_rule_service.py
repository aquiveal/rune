import pytest
from pathlib import Path
from rune.services import rule_service

def test_merge_rules_to_agents_md_creates_new_file(tmp_path):
    # Arrange
    repo_path = tmp_path
    rules_dir = repo_path / ".roo" / "rules" / "language-python"
    rules_dir.mkdir(parents=True)
    
    (rules_dir / "anti-patterns.md").write_text("# Anti-Patterns\n\nContent here.")
    
    # Act
    rule_service.merge_rules_to_agents_md(repo_path)
    
    # Assert
    agents_md = repo_path / "AGENTS.md"
    assert agents_md.exists()
    content = agents_md.read_text()
    
    assert "# Rules" in content
    assert "## language-python" in content
    assert "### Anti-Patterns" in content
    assert "Content here." in content

def test_merge_rules_to_agents_md_updates_existing_block(tmp_path):
    # Arrange
    repo_path = tmp_path
    agents_md = repo_path / "AGENTS.md"
    agents_md.write_text("Some header\n\n# Rules\n\nOld content\n\n# Another Section\n\nMore content")
    
    rules_dir = repo_path / ".roo" / "rules" / "language-python"
    rules_dir.mkdir(parents=True)
    (rules_dir / "anti-patterns.md").write_text("# Anti-Patterns\n\nContent here.")
    
    # Act
    rule_service.merge_rules_to_agents_md(repo_path)
    
    # Assert
    content = agents_md.read_text()
    assert "Some header" in content
    assert "# Rules" in content
    assert "## language-python" in content
    assert "### Anti-Patterns" in content
    assert "Old content" not in content
    assert "# Another Section" in content
    assert "More content" in content

def test_merge_rules_to_agents_md_handles_unclosed_code_blocks(tmp_path):
    # Arrange
    repo_path = tmp_path
    rules_dir = repo_path / ".roo" / "rules" / "language-python"
    rules_dir.mkdir(parents=True)
    
    (rules_dir / "anti-patterns.md").write_text("```python\ndef foo():\n    pass\n")
    (rules_dir / "other.md").write_text("Other content")
    
    # Act
    rule_service.merge_rules_to_agents_md(repo_path)
    
    # Assert
    agents_md = repo_path / "AGENTS.md"
    content = agents_md.read_text()
    
    # The unclosed code block should be closed before the next file
    assert "```python\ndef foo():\n    pass\n```" in content
    assert "Other content" in content

def test_merge_rules_to_agents_md_finds_standalone_files(tmp_path):
    # Arrange
    repo_path = tmp_path
    rules_dir = repo_path / ".agents" / "rules"
    rules_dir.mkdir(parents=True)
    
    (rules_dir / "my-rule.md").write_text("# My Rule\n\nContent here.")
    
    # Act
    rule_service.merge_rules_to_agents_md(repo_path)
    
    # Assert
    agents_md = repo_path / "AGENTS.md"
    assert agents_md.exists()
    content = agents_md.read_text()
    
    assert "# Rules" in content
    assert "## my-rule" not in content
    assert "## My Rule" in content
    assert "Content here." in content

def test_merge_rules_to_agents_md_ignores_empty_files(tmp_path):
    # Arrange
    repo_path = tmp_path
    rules_dir = repo_path / ".agents" / "rules"
    rules_dir.mkdir(parents=True)
    
    (rules_dir / "empty-rule.md").write_text("")
    (rules_dir / "whitespace-rule.md").write_text("   \n  \t  ")
    (rules_dir / "valid-rule.md").write_text("# Valid Rule\n\nContent here.")
    
    # Act
    rule_service.merge_rules_to_agents_md(repo_path)
    
    # Assert
    agents_md = repo_path / "AGENTS.md"
    assert agents_md.exists()
    content = agents_md.read_text()
    
    assert "## empty-rule" not in content
    assert "## whitespace-rule" not in content
    assert "## valid-rule" not in content
    assert "## Valid Rule" in content
