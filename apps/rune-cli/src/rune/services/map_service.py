import re
from pathlib import Path
from aider.repomap import RepoMap
from aider.io import InputOutput
from aider.models import Model
from rune.config.main import settings


def generate_submodule_map(module_path: Path, max_tokens: int | None = None) -> str:
    if max_tokens is None:
        max_tokens = settings.repomap.max_tokens

    io = InputOutput()

    # Force use gpt-4o just for the tiktoken encoding to avoid litellm gemini issues locally
    model = Model("gpt-4o")

    repo_map = RepoMap(
        map_tokens=max_tokens, root=str(module_path), main_model=model, io=io
    )

    # We want to map the entire submodule, so we treat all files as 'other_files'
    # Skip large binary folders, .git, and __pycache__
    ignore_dirs = {
        ".git",
        "__pycache__",
        "node_modules",
        "dist",
        "build",
        ".venv",
        "venv",
    }
    
    # Honor .gitignore if it exists
    gitignore_path = module_path / ".gitignore"
    spec = None
    if gitignore_path.exists():
        import pathspec
        with open(gitignore_path, "r", encoding="utf-8") as f:
            spec = pathspec.PathSpec.from_lines('gitignore', f)

    all_files = []
    
    import os
    for root, dirs, files in os.walk(module_path):
        rel_root = Path(root).relative_to(module_path)
        
        # Filter directories in-place to prevent os.walk from recursing into them
        valid_dirs = []
        for d in dirs:
            if d in ignore_dirs or d.startswith(".aider"):
                continue
                
            if spec:
                # Add trailing slash for directory matching in pathspec
                dir_rel_path = (rel_root / d).as_posix() + "/"
                if spec.match_file(dir_rel_path):
                    continue
                    
            valid_dirs.append(d)
        dirs[:] = valid_dirs
        
        for f in files:
            if any(f.startswith(ignore) for ignore in ignore_dirs):
                continue
                
            rel_file_path = (rel_root / f).as_posix()
            if spec and spec.match_file(rel_file_path):
                continue
                
            all_files.append(str(Path(root) / f))

    map_text = repo_map.get_ranked_tags_map(chat_fnames=[], other_fnames=all_files)
    return map_text or ""


def merge_ast_to_agents_md(repo_path: Path, ast_content: str) -> None:
    agents_md_path = repo_path / "AGENTS.md"
    content = ""
    if agents_md_path.exists():
        content = agents_md_path.read_text(encoding="utf-8")
        
    block = f"# Repository Map\n\n```python\n{ast_content}\n```\n"
    
    if "# Repository Map" in content:
        pattern = re.compile(r"# Repository Map\b.*?(?=\n# |\Z)", re.DOTALL)
        content = pattern.sub(lambda _: block.strip(), content)
    else:
        if content and not content.endswith("\n"):
            content += "\n\n"
        elif content:
            content += "\n"
        content += block.strip() + "\n"
        
    agents_md_path.write_text(content, encoding="utf-8")
