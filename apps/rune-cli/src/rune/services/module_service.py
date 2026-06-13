import shutil
import uuid
import os
from pathlib import Path
from typing import List, Optional, Dict
from rune.config.main import RUNE_DIR, RUNE_MODULES_DIR, get_global_rune_dir
from rune.config.exceptions import ModuleError
from rune.repositories import git_repository, module_repository, config_repository
from rune.schemas.module_schema import ModuleSchema

def add_module(root_dir: Path, url: str, path: str, name: str, type: str, agents: List[str], global_scope: bool = False, copy_mode: bool = False):
    base_dir = get_global_rune_dir() if global_scope else root_dir
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
        if not git_repository.is_git_repo(root_dir):
            raise ModuleError("Must be run inside a git repository to use submodules.")
            
        if not submodule_path.exists():
            submodule_path.parent.mkdir(parents=True, exist_ok=True)
            git_repository.add_submodule(url, str(submodule_path.relative_to(root_dir)), root_dir)
            git_repository.sparse_checkout_init(submodule_path)
            git_repository.sparse_checkout_set(submodule_path, [path])
        else:
            git_repository.sparse_checkout_add(submodule_path, [path])
            
    source_path = submodule_path / path
    if not source_path.exists():
        raise ModuleError(f"Path '{path}' not found in repository")
        
    # Deploy to agents
    for agent in agents:
        agent_path = base_dir / agent / type / name
        agent_path.parent.mkdir(parents=True, exist_ok=True)
        if agent_path.exists():
            if agent_path.is_symlink(): agent_path.unlink(missing_ok=True)
            elif agent_path.is_dir(): shutil.rmtree(agent_path)
            else: agent_path.unlink(missing_ok=True)
        
        if copy_mode:
            if source_path.is_dir():
                shutil.copytree(source_path, agent_path, symlinks=True)
            else:
                shutil.copy2(source_path, agent_path)
        else:
            try:
                os.symlink(source_path.absolute(), agent_path.absolute(), target_is_directory=source_path.is_dir())
            except OSError:
                if source_path.is_dir():
                    shutil.copytree(source_path, agent_path, symlinks=True)
                else:
                    shutil.copy2(source_path, agent_path)
                
    # Update registry
    module_repository.add_module(base_dir, ModuleSchema(name=name, url=url, path=path, type=type))

def add_git_submodule(root_dir: Path, url: str, target_dir: str):
    # Publisher workflow: add as a real git submodule
    # Extract name from URL
    name = url.rstrip('/').split('/')[-1].replace('.git', '')
    wrapper_dir = root_dir / name
    modules_dir = wrapper_dir / "modules"
    
    wrapper_dir.mkdir(parents=True, exist_ok=True)
    
    # Boilerplate SKILL.md if it's a skill
    if target_dir == "skills":
        skill_md = wrapper_dir / "SKILL.md"
        if not skill_md.exists():
            skill_md.write_text(f"---\nname: {name}\ndescription: {name} skill\n---\n# {name}\n")
            
    git_repository.add_submodule(url, str(modules_dir.relative_to(root_dir)), root_dir)

def get_status(root_dir: Path, global_scope: bool = False) -> Dict[str, str]:
    base_dir = get_global_rune_dir() if global_scope else root_dir
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
            for agent in agents:
                agent_path = base_dir / agent / mod.type / mod.name
                if not agent_path.exists():
                    mod_status = f"Missing in {agent}"
                    break
        status[f"{mod.type}/{mod.name}"] = mod_status
    return status

def remove_module(root_dir: Path, name: str, type: str, global_scope: bool = False):
    base_dir = get_global_rune_dir() if global_scope else root_dir
    # 1. Remove from agents
    agents = config_repository.get_agent_names(base_dir)
    for agent in agents:
        agent_path = base_dir / agent / type / name
        if agent_path.exists():
            if agent_path.is_symlink(): agent_path.unlink()
            else: shutil.rmtree(agent_path)
            
    # 2. Remove from registry
    module_repository.remove_module(base_dir, name)
    
    # Note: We don't automatically remove the submodule from .rune/modules/ 
    # because other rules might still be using it.

def update_modules(root_dir: Path, type: Optional[str] = None, global_scope: bool = False):
    base_dir = get_global_rune_dir() if global_scope else root_dir
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
                git_repository.run_git(["submodule", "update", "--remote", str(submodule_path.relative_to(root_dir))], cwd=root_dir)
            updated_repos.add(submodule_path)
            
        # Re-verify symlinks
        source_path = submodule_path / mod.path
        if source_path.exists():
            for agent in agents:
                agent_path = base_dir / agent / mod.type / mod.name
                if not agent_path.exists():
                    agent_path.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        os.symlink(source_path.absolute(), agent_path.absolute(), target_is_directory=source_path.is_dir())
                    except OSError:
                        if source_path.is_dir():
                            shutil.copytree(source_path, agent_path, symlinks=True)
                        else:
                            shutil.copy2(source_path, agent_path)
