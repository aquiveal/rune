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
            
    return rules
