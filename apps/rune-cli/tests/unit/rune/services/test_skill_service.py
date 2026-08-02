import pytest

from rune.schemas.skill_schema import SkillSchema
from rune.services import skill_service


def test_sanitize_skill_name():
    assert skill_service.sanitize_skill_name("My Skill!") == "my-skill"
    assert skill_service.sanitize_skill_name("---test---") == "test"


def test_validate_skill_valid(tmp_path):
    skill_dir = tmp_path / "valid-skill"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(
        "---\nname: valid-skill\ndescription: A valid skill\n---\n",
        encoding="utf-8",
    )

    skill = skill_service.validate_skill_file(skill_file)
    assert isinstance(skill, SkillSchema)
    assert skill.name == "valid-skill"


def test_validate_skill_invalid_name(tmp_path):
    skill_dir = tmp_path / "Invalid_Name"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(
        "---\nname: Invalid_Name\ndescription: Bad name\n---\n",
        encoding="utf-8",
    )

    with pytest.raises(Exception):
        skill_service.validate_skill_file(skill_file)


def test_validate_skill_name_mismatch(tmp_path):
    skill_dir = tmp_path / "folder-name"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(
        "---\nname: other-name\ndescription: Mismatched name\n---\n",
        encoding="utf-8",
    )

    with pytest.raises(Exception):
        skill_service.validate_skill_file(skill_file)


def test_validate_skill_description_too_long(tmp_path):
    skill_dir = tmp_path / "long-desc"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    desc = "a" * 2000
    skill_file.write_text(
        f"---\nname: long-desc\ndescription: {desc}\n---\n",
        encoding="utf-8",
    )

    with pytest.raises(Exception):
        skill_service.validate_skill_file(skill_file)


def test_generate_tree_with_submodule(tmp_path, monkeypatch):
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()

    submodule_dir = skill_dir / "modules" / "my-submodule"
    submodule_dir.mkdir(parents=True)
    (submodule_dir / ".git").mkdir()

    monkeypatch.setattr(
        "rune.repositories.git_repository.get_short_sha", lambda cwd: "a1b2c3d"
    )

    tree = skill_service.generate_tree(skill_dir)
    assert "my-submodule @ a1b2c3d" in tree


def test_generate_tree_with_module(tmp_path):
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()

    module_dir = skill_dir / "modules" / "foo"
    module_dir.mkdir(parents=True)
    (module_dir / "main.py").write_text("print('hello')", encoding="utf-8")

    tree = skill_service.generate_tree(skill_dir, root_dir=skill_dir)

    assert "foo" in tree
    assert "main.py" not in tree
    assert "(See AST Map below)" not in tree


def test_discover_skills_depth(tmp_path):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()

    skill1_dir = repo_path / "skills" / "skill-one"
    skill1_dir.mkdir(parents=True)
    (skill1_dir / "SKILL.md").write_text(
        "---\nname: skill-one\ndescription: desc\n---\n"
    )

    nested_skill_dir = skill1_dir / "modules" / "nested-skill"
    nested_skill_dir.mkdir(parents=True)
    (nested_skill_dir / "SKILL.md").write_text(
        "---\nname: nested-skill\ndescription: desc\n---\n"
    )

    skill2_dir = repo_path / ".agents" / "skills" / "skill-two"
    skill2_dir.mkdir(parents=True)
    (skill2_dir / "SKILL.md").write_text(
        "---\nname: skill-two\ndescription: desc\n---\n"
    )

    skills = skill_service.discover_skills(repo_path)

    skill_names = [s.name for s in skills]
    assert "skill-one" in skill_names
    assert "skill-two" in skill_names
    assert "nested-skill" not in skill_names
    assert len(skills) == 2


def test_update_skill_instructions_appends_tree_and_instructions(tmp_path):
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()

    initial_content = (
        "---\nname: test-skill\ndescription: A test skill\n---\n# test-skill\n"
    )
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        initial_content,
        encoding="utf-8",
    )

    module_dir = skill_dir / "modules" / "foo"
    module_dir.mkdir(parents=True)
    (module_dir / "main.py").write_text("print('hello')", encoding="utf-8")

    skill_service.update_skill_instructions(skill_dir)

    updated_content = skill_md.read_text(encoding="utf-8")
    assert "## File Tree" in updated_content
    assert "foo" in updated_content
    assert "> **Agent Instructions:**" in updated_content
    assert "### AST Map:" not in updated_content
    assert "(See AST Map below)" not in updated_content


def test_update_skill_instructions_creates_scaffolded_folders(tmp_path):
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()

    initial_content = "---\nname: test-skill\ndescription: Test\n---\n"
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        initial_content,
        encoding="utf-8",
    )

    skill_service.update_skill_instructions(skill_dir)

    assert (skill_dir / "scripts").is_dir()
    assert (skill_dir / "references").is_dir()
    assert (skill_dir / "assets").is_dir()
    assert (skill_dir / "modules").is_dir()

    updated_content = skill_md.read_text(encoding="utf-8")
    assert "## File Tree" in updated_content
    assert "scripts" in updated_content
    assert "modules" in updated_content
    assert "### AST Map:" not in updated_content
