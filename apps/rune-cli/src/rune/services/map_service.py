import re
from pathlib import Path

__all__ = ["generate_submodule_map", "merge_ast_to_agents_md"]


def generate_submodule_map(module_path: Path, max_tokens: int | None = None) -> str:
    rel_path = module_path.name
    return f"Directory: {rel_path} (Use probe search, query, extract, symbols on '{rel_path}')"


def merge_ast_to_agents_md(repo_path: Path, ast_content: str = "") -> None:
    agents_md_path = repo_path / "AGENTS.md"
    content = ""
    if agents_md_path.exists():
        content = agents_md_path.read_text(encoding="utf-8")

    probe_block = (
        "# Code Context Engine (Probe)\n\n"
        "Probe is configured for this workspace. Use Probe MCP tools to inspect and search code dynamically across target folder paths instead of raw static AST dumps:\n"
        '- `probe search "<query>" [path]` - Search code semantically with Elasticsearch-style syntax.\n'
        "- `probe extract <file>:<line>` - Extract complete AST semantic blocks.\n"
        '- `probe query "<pattern>"` - Perform AST structural pattern matching.\n'
        "- `probe symbols <file>` - List code symbols (functions, classes, constants) in target file.\n"
    )

    if "# Code Context Engine (Probe)" in content:
        pattern = re.compile(
            r"# Code Context Engine \(Probe\)\b.*?(?=\n# |\Z)",
            re.DOTALL,
        )
        content = pattern.sub(probe_block.strip(), content)
    elif "# Repository Map" in content:
        pattern = re.compile(
            r"# Repository Map\b.*?(?=\n# |\Z)",
            re.DOTALL,
        )
        content = pattern.sub(probe_block.strip(), content)
    else:
        if content and not content.endswith("\n"):
            content += "\n\n"
        elif content:
            content += "\n"
        content += probe_block.strip() + "\n"

    agents_md_path.write_text(content, encoding="utf-8")
