import re
from pathlib import Path

import yaml

from rune.config.exceptions import ValidationError
from rune.config.main import settings
from rune.repositories import git_repository, module_repository
from rune.schemas.skill_schema import SkillSchema

__all__ = [
    "discover_skills",
    "ensure_skill_md",
    "generate_tree",
    "sanitize_skill_name",
    "update_skill_instructions",
    "validate_skill_file",
]


def sanitize_skill_name(name: str) -> str:
    """Sanitize a string to be a valid skill name."""
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    name = name.strip("-")
    name = re.sub(r"-+", "-", name)
    return name


def ensure_skill_md(skill_dir: Path) -> Path:
    """Ensure SKILL.md exists in skill_dir with valid frontmatter."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists() and skill_dir.is_dir():
        name = sanitize_skill_name(skill_dir.name)
        if name:
            description = f"Provides specialized context, rules, and tools for implementing, configuring, and debugging {name}."
            skill_md.write_text(
                f"---\nname: {name}\ndescription: {description}\n---\n# {name}\n",
                encoding="utf-8",
            )
    return skill_md


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
        except Exception as e:  # noqa: BLE001
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
    except Exception as e:  # noqa: BLE001
        raise ValidationError(f"Validation failed: {e}")


def discover_skills(repo_path: Path) -> list[SkillSchema]:
    skills = []
    # Search in configured skill locations
    search_paths = [repo_path / Path(p) for p in settings.get_skill_search_paths()]

    # First check subdirectories in common skill locations and ensure SKILL.md exists
    for p in search_paths:
        if p.exists() and p.is_dir():
            for item in p.iterdir():
                if item.is_dir() and not item.name.startswith("."):
                    ensure_skill_md(item)

    # Search for SKILL.md directly in search paths or one level deep
    found_files = []
    if (repo_path / "SKILL.md").exists():
        found_files.append(repo_path / "SKILL.md")

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
    ignore: list[str] | None = None,
    ast_maps: dict | None = None,
    root_dir: Path | None = None,
    max_depth: int = 3,
    current_depth: int = 0,
    modules_map: dict | None = None,
) -> str:
    if ignore is None:
        ignore = [
            ".git",
            "__pycache__",
            "node_modules",
            ".venv",
            "venv",
            ".env",
            ".repomap.txt",
        ]
    if ast_maps is None:
        ast_maps = {}
    if modules_map is None:
        modules_map = {}
    if root_dir is None:
        root_dir = dir_path

    if current_depth >= max_depth:
        return ""

    tree_str = ""
    paths = sorted(dir_path.iterdir(), key=lambda p: (p.is_file(), p.name))
    paths = [p for p in paths if p.name not in ignore]

    for i, path in enumerate(paths):
        is_last = i == len(paths) - 1
        connector = "└── " if is_last else "├── "

        if path.parent.name == "modules" and path.is_dir():
            rel_path = str(path.relative_to(root_dir)).replace("\\", "/")
            url = modules_map.get(rel_path) or modules_map.get(path.name)
            if url:
                tree_str += f"{prefix}{connector}{path.name} ({url.strip()})\n"
            elif (path / ".git").exists():
                sha = git_repository.get_short_sha(path)
                suffix = f" @ {sha}" if sha else " @ submodule"
                tree_str += f"{prefix}{connector}{path.name}{suffix}\n"
            else:
                tree_str += f"{prefix}{connector}{path.name}\n"
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
                    path,
                    prefix + extension,
                    ignore,
                    ast_maps,
                    root_dir,
                    max_depth,
                    current_depth + 1,
                    modules_map,
                )

    return tree_str


def update_skill_instructions(skill_dir: Path):
    ensure_skill_md(skill_dir)
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return

    scaffold_folders = ["scripts", "references", "assets", "modules"]
    for folder in scaffold_folders:
        (skill_dir / folder).mkdir(exist_ok=True)

    repo_root = git_repository.get_git_root(skill_dir) or skill_dir
    registered_modules = module_repository.list_modules(repo_root)
    modules_map = {}
    for mod in registered_modules:
        clean_url = mod.base_url.strip()
        modules_map[mod.path.strip()] = clean_url
        modules_map[Path(mod.path).name.strip()] = clean_url

    tree = generate_tree(skill_dir, root_dir=skill_dir, modules_map=modules_map)
    content = skill_md.read_text(encoding="utf-8")

    tree_block = f"## File Tree\n\n```text\n{skill_dir.name}/\n{tree}```\n"

    modules_dir = skill_dir / "modules"
    if modules_dir.exists() and any(modules_dir.iterdir()):
        tree_block += (
            "\n> **Agent Instructions:** The `modules/` directory contains full source code repositories. "
            "Probe is configured for this workspace. Use Probe MCP tools to inspect and search code dynamically "
            "across target folder paths instead of raw static AST dumps:\n"
            '> - `probe search "<query>" [path]` - Search code semantically with Elasticsearch-style syntax.\n'
            "> - `probe extract <file>:<line>` - Extract complete AST semantic blocks.\n"
            '> - `probe query "<pattern>"` - Perform AST structural pattern matching.\n'
            "> - `probe symbols <file>` - List code symbols (functions, classes, constants) in target file.\n"
        )

    if "## File Tree" in content:
        pattern = re.compile(r"## File Tree.*?(?=\n## |\Z)", re.DOTALL)
        content = pattern.sub(lambda _: tree_block.strip(), content)
    else:
        content += f"\n{tree_block.strip()}\n"

    skill_md.write_text(content, encoding="utf-8")
