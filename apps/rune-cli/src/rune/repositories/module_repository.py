from pathlib import Path
from typing import List, Dict
from rune.repositories import git_repository
from rune.config.main import RUNE_MODULES_FILE
from rune.schemas.module_schema import ModuleSchema

def _get_modules_path(root_dir: Path) -> Path:
    return root_dir / RUNE_MODULES_FILE

def list_modules(root_dir: Path) -> List[ModuleSchema]:
    path = _get_modules_path(root_dir)
    if not path.exists():
        return []
    
    try:
        # We use git config --list to parse the .runemodules file
        result = git_repository.run_git(["config", "--file", str(path), "--list"])
    except Exception:
        return []

    modules_dict = {}
    for line in result.stdout.strip().split('\n'):
        if not line: continue
        key, value = line.split('=', 1)
        if key.startswith('runemodule.'):
            parts = key.split('.')
            if len(parts) >= 3:
                mod_id = '.'.join(parts[1:-1])
                prop = parts[-1]
                if mod_id not in modules_dict:
                    modules_dict[mod_id] = {"name": mod_id}
                modules_dict[mod_id][prop] = value
    
    return [ModuleSchema(**m) for m in modules_dict.values() if "url" in m and "path" in m]

def add_module(root_dir: Path, module: ModuleSchema):
    path = _get_modules_path(root_dir)
    section = f'runemodule."{module.name}"'
    git_repository.set_config(f"{section}.url", module.url, path)
    git_repository.set_config(f"{section}.path", module.path, path)

def remove_module(root_dir: Path, module_name: str):
    path = _get_modules_path(root_dir)
    git_repository.unset_config_section(f'runemodule."{module_name}"', path)
