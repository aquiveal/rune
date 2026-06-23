import yaml
import re
from pathlib import Path
from typing import List, Optional
from rune.schemas.skill_schema import SkillSchema
from rune.config.exceptions import ValidationError
from rune.repositories import git_repository


def sanitize_skill_name(name: str) -> str:
    """Sanitize a string to be a valid skill name."""
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    name = name.strip("-")
    name = re.sub(r"-+", "-", name)
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
            raise ValidationError(
                f"Skill name '{skill.name}' must exactly match the parent directory name '{parent_dir_name}'"
            )

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
            skill.path = str(skill_file.parent.relative_to(repo_path)).replace(
                "\\", "/"
            )
            if skill.path == ".":
                skill.path = ""
            skills.append(skill)
        except ValidationError:
            continue

    return skills


def generate_tree(
    dir_path: Path,
    prefix: str = "",
    ignore: Optional[List[str]] = None,
    ast_maps: Optional[dict] = None,
    root_dir: Optional[Path] = None,
) -> str:
    if ignore is None:
        ignore = [".git", "__pycache__", "node_modules", ".venv", "venv", ".env"]
    if ast_maps is None:
        ast_maps = {}
    if root_dir is None:
        root_dir = dir_path

    tree_str = ""
    paths = sorted(dir_path.iterdir(), key=lambda p: (p.is_file(), p.name))
    paths = [p for p in paths if p.name not in ignore]

    for i, path in enumerate(paths):
        is_last = i == len(paths) - 1
        connector = "└── " if is_last else "├── "

        repomap_file = path / ".repomap.txt"
        if path.is_dir() and repomap_file.exists():
            map_content = repomap_file.read_text(encoding="utf-8")
            rel_path = str(path.relative_to(root_dir)).replace("\\", "/")
            ast_maps[rel_path] = map_content.strip()
            tree_str += f"{prefix}{connector}{path.name} (See AST Map below)\n"
            continue

        if path.is_dir() and (path / ".git").exists():
            sha = git_repository.get_short_sha(path)
            suffix = f" @ {sha}" if sha else " @ submodule"
            tree_str += f"{prefix}{connector}{path.name}{suffix}\n"
        else:
            tree_str += f"{prefix}{connector}{path.name}\n"
            if path.is_dir():
                extension = "    " if is_last else "│   "
                tree_str += generate_tree(
                    path, prefix + extension, ignore, ast_maps, root_dir
                )

    return tree_str


def update_skill_tree(skill_dir: Path):
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return

    ast_maps = {}
    tree = generate_tree(skill_dir, ast_maps=ast_maps, root_dir=skill_dir)
    content = skill_md.read_text(encoding="utf-8")

    tree_block = f"## File Tree\n\n```text\n{skill_dir.name}/\n{tree}```\n"

    if ast_maps:
        tree_block += "\n> **Agent Instructions:** The AST maps below provide a high-level overview of the `modules/` directory. Note that the complete repository source code is available within the `modules/` folder. You can and should use your file reading tools to access the actual source code within `modules/` for complete details, implementation logic, and context beyond what the AST map provides.\n"
        for rel_path, map_content in ast_maps.items():
            tree_block += (
                f"\n### AST Map: `{rel_path}`\n\n```python\n{map_content}\n```\n"
            )

    if "## File Tree" in content:
        pattern = re.compile(r"## File Tree.*?(?=\n## |\Z)", re.DOTALL)
        content = pattern.sub(lambda _: tree_block.strip(), content)
    else:
        content += f"\n{tree_block.strip()}\n"

    skill_md.write_text(content, encoding="utf-8")
