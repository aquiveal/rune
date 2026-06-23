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
    all_files = [
        str(p)
        for p in module_path.rglob("*")
        if p.is_file()
        and not any(
            part in ignore_dirs or part.startswith(".aider") for part in p.parts
        )
    ]

    map_text = repo_map.get_ranked_tags_map(chat_fnames=[], other_fnames=all_files)
    return map_text or ""
