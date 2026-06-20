from pathlib import Path
from aider.repomap import RepoMap
from aider.io import InputOutput
from rune.repositories import config_repository, git_repository

def generate_submodule_map(module_path: Path, max_tokens: int = 1000) -> str:
    # Determine model from rune config, default to gemini/gemini-3.1-flash-lite
    git_root = git_repository.get_git_root(module_path) or module_path
    model_name = config_repository.get_repomap_model(git_root)
    
    io = InputOutput()
    repo_map = RepoMap(
        map_tokens=max_tokens,
        root=str(module_path),
        main_model=model_name,
        io=io
    )
    
    # We want to map the entire submodule, so we treat all files as 'other_files'
    # Skip large binary folders, .git, and __pycache__
    ignore_dirs = {'.git', '__pycache__', 'node_modules', 'dist', 'build', '.venv', 'venv'}
    all_files = [
        str(p) for p in module_path.rglob("*") 
        if p.is_file() and not any(part in ignore_dirs for part in p.parts)
    ]
    
    map_text = repo_map.get_ranked_tags_map(
        chat_files=[],
        other_files=all_files
    )
    return map_text
