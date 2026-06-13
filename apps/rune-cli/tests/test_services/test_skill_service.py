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
