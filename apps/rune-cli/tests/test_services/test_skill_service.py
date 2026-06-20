import pytest
from pathlib import Path
from rune.services import skill_service
from rune.config.exceptions import ValidationError

def test_sanitize_skill_name():
    assert skill_service.sanitize_skill_name("My Skill") == "my-skill"
    assert skill_service.sanitize_skill_name("skill_name") == "skill-name"
    assert skill_service.sanitize_skill_name("Skill@Name!") == "skill-name"
    assert skill_service.sanitize_skill_name("---skill---") == "skill"
    assert skill_service.sanitize_skill_name("a") == "a"
    assert skill_service.sanitize_skill_name("  spaces  ") == "spaces"
    assert skill_service.sanitize_skill_name("multiple---hyphens") == "multiple-hyphens"
    assert skill_service.sanitize_skill_name("!@#$%^&*()") == ""

def test_validate_skill_valid(tmp_path):
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text("---\nname: test-skill\ndescription: A valid test skill\n---\n", encoding="utf-8")
    
    skill = skill_service.validate_skill_file(skill_file)
    assert skill.name == "test-skill"

def test_validate_skill_invalid_name(tmp_path):
    skill_dir = tmp_path / "Invalid_Name"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    
    # Uppercase not allowed
    skill_file.write_text("---\nname: Invalid-Name\ndescription: desc\n---\n")
    with pytest.raises(ValidationError, match="name"):
        skill_service.validate_skill_file(skill_file)

    # Starts with hyphen
    skill_file.write_text("---\nname: -invalid\ndescription: desc\n---\n")
    with pytest.raises(ValidationError, match="name"):
        skill_service.validate_skill_file(skill_file)

    # Consecutive hyphens
    skill_file.write_text("---\nname: invalid--name\ndescription: desc\n---\n")
    with pytest.raises(ValidationError, match="name"):
        skill_service.validate_skill_file(skill_file)

def test_validate_skill_name_mismatch(tmp_path):
    skill_dir = tmp_path / "actual-name"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text("---\nname: mismatched-name\ndescription: desc\n---\n")
    
    with pytest.raises(ValidationError, match="match the parent directory name"):
        skill_service.validate_skill_file(skill_file)

def test_validate_skill_description_too_long(tmp_path):
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    long_desc = "a" * 1025
    skill_file.write_text(f"---\nname: test-skill\ndescription: {long_desc}\n---\n")
    
    with pytest.raises(ValidationError, match="description"):
        skill_service.validate_skill_file(skill_file)

def test_generate_tree_with_submodule(tmp_path, monkeypatch):
    # Create a mock directory structure
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()
    
    # Normal directory
    normal_dir = skill_dir / "normal_dir"
    normal_dir.mkdir()
    (normal_dir / "file.txt").write_text("content")
    
    # Submodule directory
    submodule_dir = skill_dir / "submodule_dir"
    submodule_dir.mkdir()
    (submodule_dir / ".git").write_text("gitdir: ../.git/modules/submodule_dir")
    (submodule_dir / "should_not_be_seen.txt").write_text("content")
    
    # Mock git_repository.get_short_sha
    def mock_get_short_sha(cwd):
        if cwd.name == "submodule_dir":
            return "a1b2c3d"
        return None
        
    monkeypatch.setattr("rune.repositories.git_repository.get_short_sha", mock_get_short_sha)
    
    tree = skill_service.generate_tree(skill_dir)
    
    # Assertions
    assert "normal_dir" in tree
    assert "file.txt" in tree
    assert "submodule_dir @ a1b2c3d" in tree
    assert "should_not_be_seen.txt" not in tree

def test_generate_tree_with_ast_map(tmp_path):
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()
    
    # Create module with repomap
    module_dir = skill_dir / "modules" / "foo"
    module_dir.mkdir(parents=True)
    
    mock_repomap_content = "src/foo/__init__.py:\n│__version__ = '1.0'\n"
    (module_dir / ".repomap.txt").write_text(mock_repomap_content, encoding="utf-8")
    
    ast_maps = {}
    tree = skill_service.generate_tree(skill_dir, ast_maps=ast_maps, root_dir=skill_dir)
    
    assert "foo (See AST Map below)" in tree
    assert "modules/foo" in ast_maps
    assert ast_maps["modules/foo"] == mock_repomap_content.strip()

def test_discover_skills_depth(tmp_path):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    
    # Create a top-level skill
    skill1_dir = repo_path / "skills" / "skill-one"
    skill1_dir.mkdir(parents=True)
    (skill1_dir / "SKILL.md").write_text("---\nname: skill-one\ndescription: desc\n---\n")
    
    # Create a nested skill (should NOT be discovered)
    nested_skill_dir = skill1_dir / "modules" / "nested-skill"
    nested_skill_dir.mkdir(parents=True)
    (nested_skill_dir / "SKILL.md").write_text("---\nname: nested-skill\ndescription: desc\n---\n")
    
    # Create a skill in .agents/skills
    skill2_dir = repo_path / ".agents" / "skills" / "skill-two"
    skill2_dir.mkdir(parents=True)
    (skill2_dir / "SKILL.md").write_text("---\nname: skill-two\ndescription: desc\n---\n")
    
    skills = skill_service.discover_skills(repo_path)
    
    skill_names = [s.name for s in skills]
    assert "skill-one" in skill_names
    assert "skill-two" in skill_names
    assert "nested-skill" not in skill_names
    assert len(skills) == 2
