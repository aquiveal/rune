import yaml
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from rune.schemas.skill_schema import SkillSchema, SkillMetadata
from rune.config.exceptions import ValidationError

def validate_skill_file(path: Path) -> SkillSchema:
    if not path.exists():
        raise ValidationError(f"SKILL.md not found at {path}")

    try:
        content = path.read_text(encoding="utf-8")
        if not content.startswith("---"):
            raise ValidationError("Missing YAML frontmatter")
            
        parts = content.split("---", 2)
        if len(parts) < 3:
            raise ValidationError("Invalid YAML frontmatter format")
            
        frontmatter = yaml.safe_load(parts[1])
        if not isinstance(frontmatter, dict):
            raise ValidationError("Frontmatter must be a YAML dictionary")

        try:
            skill = SkillSchema(**frontmatter)
        except Exception as e:
            raise ValidationError(f"Schema validation failed: {e}")

        # Check if name matches parent directory name
        parent_dir_name = path.parent.name
        if skill.name != parent_dir_name:
            raise ValidationError(f"Skill name '{skill.name}' must exactly match the parent directory name '{parent_dir_name}'")

        return skill
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Validation failed: {e}")

def discover_skills(repo_path: Path) -> List[SkillSchema]:
    skills = []
    # Search in common locations
    search_paths = [
        repo_path,
        repo_path / "skills",
        repo_path / ".claude" / "skills",
        repo_path / ".roo" / "skills",
    ]
    
    # Also recursive search if nothing found in common locations
    found_files = []
    for p in search_paths:
        if p.exists() and p.is_dir():
            found_files.extend(list(p.glob("**/SKILL.md")))
    
    # Deduplicate by path
    seen_paths = set()
    for skill_file in found_files:
        abs_path = skill_file.absolute()
        if abs_path in seen_paths:
            continue
        seen_paths.add(abs_path)
        
        try:
            skill = validate_skill_file(skill_file)
            # Set relative path from repo root
            skill.path = str(skill_file.parent.relative_to(repo_path)).replace('\\', '/')
            if skill.path == ".":
                skill.path = ""
            skills.append(skill)
        except ValidationError:
            continue
            
    return skills
