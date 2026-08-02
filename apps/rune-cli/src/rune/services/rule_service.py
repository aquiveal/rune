import yaml
from pathlib import Path
from typing import List
from rune.schemas.rule_schema import RuleSchema
from rune.config.main import settings
from rune.config.exceptions import ValidationError


def validate_rule_file(path: Path) -> RuleSchema:
    # Rules might be .clinerules or RULE.md or similar
    # For now, let's assume they also use YAML frontmatter if they are RULE.md
    if not path.exists():
        raise ValidationError(f"Rule file not found at {path}")

    try:
        content = path.read_text(encoding="utf-8")
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])
                if isinstance(frontmatter, dict):
                    return RuleSchema(**frontmatter)

        # Fallback for files without frontmatter (like .clinerules)
        return RuleSchema(name=path.name, description=f"Rule from {path.name}")
    except Exception as e:
        raise ValidationError(f"Validation failed: {e}")


def discover_rules(repo_path: Path) -> List[RuleSchema]:
    rules = []
    # Search for .clinerules, .cursorrules, and RULE.md
    patterns = [".clinerules", ".cursorrules", "RULE.md", "rules/*.md"]

    found_files = []
    for pattern in patterns:
        found_files.extend(list(repo_path.glob(f"**/{pattern}")))

    seen_paths = set()
    for rule_file in found_files:
        abs_path = rule_file.absolute()
        if abs_path in seen_paths:
            continue
        seen_paths.add(abs_path)

        try:
            rule = validate_rule_file(rule_file)
            rule.path = str(rule_file.relative_to(repo_path)).replace("\\", "/")
            rules.append(rule)
        except ValidationError:
            continue

    # Also discover directories inside 'rules/'
    rules_dir = repo_path / "rules"
    if rules_dir.exists() and rules_dir.is_dir():
        for child in rules_dir.iterdir():
            if child.is_dir():
                abs_path = child.absolute()
                if abs_path not in seen_paths:
                    seen_paths.add(abs_path)
                    rule = RuleSchema(
                        name=child.name,
                        description=f"Rule directory {child.name}",
                        path=f"rules/{child.name}",
                    )
                    rules.append(rule)

    return rules


def discover_rule_dirs(repo_path: Path) -> List[Path]:
    rule_dirs = []
    rule_search_paths = settings.get_rule_search_paths()

    for rel_path in rule_search_paths:
        rules_dir = repo_path / Path(rel_path)
        if rules_dir.exists() and rules_dir.is_dir():
            # The rules can be subdirectories or standalone markdown files
            for child in rules_dir.iterdir():
                if child.is_dir() or (child.is_file() and child.suffix == ".md"):
                    rule_dirs.append(child)

    return rule_dirs


def merge_rules_to_agents_md(repo_path: Path):
    rule_dirs = discover_rule_dirs(repo_path)
    if not rule_dirs:
        return

    rules_block = "# Rules\n\n"

    for rule_item in rule_dirs:
        if rule_item.is_dir():
            md_files = sorted(rule_item.glob("*.md"))
            if not md_files:
                continue

            # Filter out empty files
            valid_files = []
            for md_file in md_files:
                content = md_file.read_text(encoding="utf-8").strip()
                if content:
                    valid_files.append((md_file, content))

            if not valid_files:
                continue

            rules_block += f"## {rule_item.name}\n\n"

            for md_file, content in valid_files:
                # Strip frontmatter if present
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        content = parts[2].strip()

                # Shift headings in the content by 2 levels to maintain hierarchy under ## {rule_item.name}
                # e.g., # Heading -> ### Heading
                import re

                content = re.sub(r"^(#+)\s", r"##\1 ", content, flags=re.MULTILINE)

                # Handle unclosed code blocks
                code_block_count = len(
                    re.findall(r"^\s*```", content, flags=re.MULTILINE)
                )
                if code_block_count % 2 != 0:
                    content += "\n```"

                rules_block += f"{content}\n\n"
        elif rule_item.is_file() and rule_item.suffix == ".md":
            content = rule_item.read_text(encoding="utf-8").strip()
            if not content:
                continue

            # Strip frontmatter if present
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    content = parts[2].strip()

            # Shift headings in the content by 1 level to maintain hierarchy under # Rules
            import re

            content = re.sub(r"^(#+)\s", r"#\1 ", content, flags=re.MULTILINE)

            # Handle unclosed code blocks
            code_block_count = len(re.findall(r"^\s*```", content, flags=re.MULTILINE))
            if code_block_count % 2 != 0:
                content += "\n```"

            rules_block += f"{content}\n\n"

    agents_md = repo_path / "AGENTS.md"

    if agents_md.exists():
        content = agents_md.read_text(encoding="utf-8")
        # Try to find existing # Rules block
        import re

        # Match from # Rules until the next # (h1) or end of file
        pattern = re.compile(r"# Rules\b.*?(?=\n# |\Z)", re.DOTALL)
        if pattern.search(content):
            new_content = pattern.sub(rules_block.strip(), content)
        else:
            # If no block found, append it
            new_content = content.rstrip() + "\n\n" + rules_block.strip() + "\n"
        agents_md.write_text(new_content, encoding="utf-8")
    else:
        agents_md.write_text(rules_block, encoding="utf-8")
