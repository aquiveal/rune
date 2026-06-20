import yaml
import re
from pathlib import Path
from typing import List
from rune.schemas.skill_schema import SkillSchema, SkillMetadata
from rune.config.exceptions import ValidationError
from rune.repositories import git_repository

def sanitize_skill_name(name: str) -> str:
    """Sanitize a string to be a valid skill name."""
    name = name.lower()
    name = re.sub(r'[^a-z0-9]+', '-', name)
    name = name.strip('-')
    name = re.sub(r'-+', '-', name)
    return name

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
        repo_path / ".agents" / "skills",
    ]
    
    # Search for SKILL.md directly in the search paths or one level deep
    found_files = []
    for p in search_paths:
        if p.exists() and p.is_dir():
            found_files.extend(list(p.glob("SKILL.md")))
            found_files.extend(list(p.glob("*/SKILL.md")))
    
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

def generate_tree(dir_path: Path, prefix: str = "", ignore: List[str] = None) -> str:
    if ignore is None:
        ignore = [".git", "__pycache__", "node_modules", ".venv", "venv", ".env"]
    
    tree_str = ""
    paths = sorted(dir_path.iterdir(), key=lambda p: (p.is_file(), p.name))
    paths = [p for p in paths if p.name not in ignore]
    
    for i, path in enumerate(paths):
        is_last = i == len(paths) - 1
        connector = "└── " if is_last else "├── "
        
        repomap_file = path / ".repomap.txt"
        if path.is_dir() and repomap_file.exists():
            map_content = repomap_file.read_text(encoding="utf-8")
            tree_str += f"{prefix}{connector}{path.name} (AST Map)\n"
            
            extension = "    " if is_last else "│   "
            indented_map = "\n".join(f"{prefix}{extension}{line}" for line in map_content.splitlines() if line.strip())
            tree_str += indented_map + "\n"
            continue
            
        if path.is_dir() and (path / ".git").exists():
            sha = git_repository.get_short_sha(path)
            suffix = f" @ {sha}" if sha else " @ submodule"
            tree_str += f"{prefix}{connector}{path.name}{suffix}\n"
        else:
            tree_str += f"{prefix}{connector}{path.name}\n"
            if path.is_dir():
                extension = "    " if is_last else "│   "
                tree_str += generate_tree(path, prefix + extension, ignore)
            
    return tree_str

def update_skill_tree(skill_dir: Path):
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return
        
    tree = generate_tree(skill_dir)
    content = skill_md.read_text(encoding="utf-8")
    
    tree_block = f"## File Tree\n\n```text\n{skill_dir.name}/\n{tree}```\n"
    
    if "## File Tree" in content:
        pattern = re.compile(r"## File Tree.*?(?=\n## |\Z)", re.DOTALL)
        content = pattern.sub(lambda _: tree_block.strip(), content)
    else:
        content += f"\n{tree_block}"
        
    skill_md.write_text(content, encoding="utf-8")
