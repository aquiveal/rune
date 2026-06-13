import yaml
from pathlib import Path
from typing import List, Optional
from rune.schemas.rule_schema import RuleSchema
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
            rule.path = str(rule_file.relative_to(repo_path)).replace('\\', '/')
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
                    rule = RuleSchema(name=child.name, description=f"Rule directory {child.name}", path=f"rules/{child.name}")
                    rules.append(rule)
            
    return rules

def discover_rule_dirs(repo_path: Path) -> List[Path]:
    rule_dirs = []
    # Search for directories named 'rules' inside agent folders
    agent_folders = [".roo", ".claude", ".cursor", ".cline", ".agents"]
    
    for folder in agent_folders:
        rules_dir = repo_path / folder / "rules"
        if rules_dir.exists() and rules_dir.is_dir():
            # The rules are subdirectories inside the 'rules' folder
            for child in rules_dir.iterdir():
                if child.is_dir():
                    rule_dirs.append(child)
                    
    return rule_dirs

def merge_rules_to_agents_md(repo_path: Path):
    rule_dirs = discover_rule_dirs(repo_path)
    if not rule_dirs:
        return
        
    merged_content = "# Agent Rules\n\n"
    
    for rule_dir in rule_dirs:
        md_files = sorted(rule_dir.glob("*.md"))
        if not md_files:
            continue
            
        merged_content += f"## {rule_dir.name}\n\n"
        
        for md_file in md_files:
            content = md_file.read_text(encoding="utf-8")
            # Strip frontmatter if present
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    content = parts[2].strip()
            
            merged_content += f"### {md_file.name}\n\n{content}\n\n"
            
    agents_md = repo_path / "AGENTS.md"
    agents_md.write_text(merged_content, encoding="utf-8")
