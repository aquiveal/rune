import shutil
import uuid
import os
from pathlib import Path
from typing import List, Optional, Dict
from rune.config.main import RUNE_DIR, RUNE_MODULES_DIR, RUNE_TMP_DIR, get_global_rune_dir
from rune.config.exceptions import ModuleError
from rune.repositories import git_repository, module_repository, config_repository
from rune.schemas.module_schema import ModuleSchema

def add_module(git_root: Path, cwd: Path, url: str, path: str, name: str, type: str, agents: List[str], global_scope: bool = False, copy_mode: bool = False):
    base_dir = get_global_rune_dir() if global_scope else git_root
    rune_dir = base_dir / RUNE_DIR
    
    repo_name = url.rstrip('/').split('/')[-1].replace('.git', '')
    submodule_path = rune_dir / RUNE_MODULES_DIR / type / repo_name
    
    if global_scope:
        # Global scope uses standard clone since it's not a project repo
        if not submodule_path.exists():
            submodule_path.parent.mkdir(parents=True, exist_ok=True)
            git_repository.clone(url, submodule_path)
            git_repository.sparse_checkout_init(submodule_path)
            git_repository.sparse_checkout_set(submodule_path, [path])
        else:
            git_repository.sparse_checkout_add(submodule_path, [path])
    else:
        # Local scope uses submodules
        if not git_repository.is_git_repo(git_root):
            raise ModuleError("Must be run inside a git repository to use submodules.")
            
        if not submodule_path.exists():
            submodule_path.parent.mkdir(parents=True, exist_ok=True)
            git_repository.add_submodule(url, str(submodule_path.relative_to(git_root)), git_root, force=True)
            git_repository.sparse_checkout_init(submodule_path)
            git_repository.sparse_checkout_set(submodule_path, [path])
        else:
            git_repository.sparse_checkout_add(submodule_path, [path])
            
    source_path = submodule_path / path
    if not source_path.exists():
        raise ModuleError(f"Path '{path}' not found in repository")
        
    # Deploy to agents or cwd
    target_paths = []
    if global_scope or cwd == git_root:
        for agent in agents:
            target_paths.append(base_dir / agent / type / name)
    else:
        target_paths.append(cwd / type / name)
        
    for agent_path in target_paths:
        agent_path.parent.mkdir(parents=True, exist_ok=True)
        if agent_path.exists():
            if agent_path.is_symlink(): agent_path.unlink(missing_ok=True)
            elif agent_path.is_dir(): shutil.rmtree(agent_path)
            else: agent_path.unlink(missing_ok=True)
        
        # Always copy instead of symlink to avoid cross-OS issues (Windows + WSL)
        if source_path.is_dir():
            shutil.copytree(source_path, agent_path, dirs_exist_ok=True)
        else:
            shutil.copy2(source_path, agent_path)
                
    # Update registry
    module_repository.add_module(base_dir, ModuleSchema(name=name, url=url, path=path, type=type))

def get_status(git_root: Path, global_scope: bool = False) -> Dict[str, str]:
    base_dir = get_global_rune_dir() if global_scope else git_root
    modules = module_repository.list_modules(base_dir)
    agents = config_repository.get_agent_names(base_dir)
    
    status = {}
    for mod in modules:
        mod_status = "OK"
        repo_name = mod.url.rstrip('/').split('/')[-1].replace('.git', '')
        cache_path = base_dir / RUNE_DIR / RUNE_MODULES_DIR / mod.type / repo_name / mod.path
        if not cache_path.exists():
            mod_status = "Missing Cache"
        else:
            # We only check agent paths for status, not custom cwd paths
            for agent in agents:
                agent_path = base_dir / agent / mod.type / mod.name
                if not agent_path.exists():
                    mod_status = f"Missing in {agent}"
                    break
        status[f"{mod.type}/{mod.name}"] = mod_status
    return status

def remove_module(git_root: Path, name: str, type: str, global_scope: bool = False):
    base_dir = get_global_rune_dir() if global_scope else git_root
    # 1. Remove from agents
    agents = config_repository.get_agent_names(base_dir)
    for agent in agents:
        agent_path = base_dir / agent / type / name
        if agent_path.exists():
            if agent_path.is_symlink(): agent_path.unlink(missing_ok=True)
            else: shutil.rmtree(agent_path)
            
    # 2. Remove from registry
    module_repository.remove_module(base_dir, name)
    
    # Note: We don't automatically remove the submodule from .rune/modules/ 
    # because other rules might still be using it.

def update_modules(git_root: Path, type: Optional[str] = None, global_scope: bool = False):
    base_dir = get_global_rune_dir() if global_scope else git_root
    modules = module_repository.list_modules(base_dir)
    agents = config_repository.get_agent_names(base_dir)
    
    if type:
        modules = [m for m in modules if m.type == type]
        
    updated_repos = set()
    
    for mod in modules:
        repo_name = mod.url.rstrip('/').split('/')[-1].replace('.git', '')
        submodule_path = base_dir / RUNE_DIR / RUNE_MODULES_DIR / mod.type / repo_name
        
        if submodule_path not in updated_repos:
            if global_scope:
                git_repository.run_git(["pull"], cwd=submodule_path)
            else:
                git_repository.run_git(["submodule", "update", "--remote", str(submodule_path.relative_to(git_root))], cwd=git_root)
            updated_repos.add(submodule_path)
            
        # Re-verify and copy (only for agent paths, custom cwd paths are not tracked for updates)
        source_path = submodule_path / mod.path
        if source_path.exists():
            for agent in agents:
                agent_path = base_dir / agent / mod.type / mod.name
                if not agent_path.exists():
                    agent_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Always copy instead of symlink
                if agent_path.exists():
                    if agent_path.is_symlink(): agent_path.unlink(missing_ok=True)
                    elif agent_path.is_dir(): shutil.rmtree(agent_path)
                    else: agent_path.unlink(missing_ok=True)
                    
                if source_path.is_dir():
                    shutil.copytree(source_path, agent_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(source_path, agent_path)
