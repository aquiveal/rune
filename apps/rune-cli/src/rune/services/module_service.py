import shutil
import uuid
import os
from pathlib import Path
from typing import List, Optional, Dict
from rune.config.main import RUNE_DIR, RUNE_MODULES_DIR, RUNE_TMP_DIR, get_global_rune_dir
from rune.config.exceptions import ModuleError
from rune.repositories import git_repository, module_repository, config_repository
from rune.schemas.module_schema import ModuleSchema

def add_module(root_dir: Path, url: str, path: str, name: str, type: str, agents: List[str], global_scope: bool = False, copy_mode: bool = False):
    base_dir = get_global_rune_dir() if global_scope else root_dir
    rune_dir = base_dir / RUNE_DIR
    
    # 1. Fetch to tmp
    tmp_id = str(uuid.uuid4())
    tmp_dir = rune_dir / RUNE_TMP_DIR / tmp_id
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        git_repository.clone(url, tmp_dir, depth=1)
        
        source_path = tmp_dir / path
        if not source_path.exists():
            raise ModuleError(f"Path '{path}' not found in repository")
            
        # 2. Cache in .rune/modules
        target_path = rune_dir / RUNE_MODULES_DIR / type / name
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if target_path.exists():
            if target_path.is_dir(): shutil.rmtree(target_path)
            else: target_path.unlink()
            
        if source_path.is_dir():
            shutil.copytree(source_path, target_path, ignore=shutil.ignore_patterns('.git'), symlinks=True)
        else:
            shutil.copy2(source_path, target_path)
        
        # 3. Deploy to agents
        for agent in agents:
            agent_path = base_dir / agent / type / name
            agent_path.parent.mkdir(parents=True, exist_ok=True)
            if agent_path.exists():
                if agent_path.is_symlink(): agent_path.unlink()
                elif agent_path.is_dir(): shutil.rmtree(agent_path)
                else: agent_path.unlink()
            
            if copy_mode:
                if target_path.is_dir():
                    shutil.copytree(target_path, agent_path, symlinks=True)
                else:
                    shutil.copy2(target_path, agent_path)
            else:
                try:
                    os.symlink(target_path.absolute(), agent_path.absolute(), target_is_directory=target_path.is_dir())
                except OSError:
                    if target_path.is_dir():
                        shutil.copytree(target_path, agent_path, symlinks=True)
                    else:
                        shutil.copy2(target_path, agent_path)
                    
        # 4. Update registry
        module_repository.add_module(base_dir, ModuleSchema(name=name, url=url, path=path, type=type))
        
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

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
        cache_path = base_dir / RUNE_DIR / RUNE_MODULES_DIR / mod.type / mod.name
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
            
    # 2. Remove from cache
    cache_path = base_dir / RUNE_DIR / RUNE_MODULES_DIR / type / name
    if cache_path.exists():
        shutil.rmtree(cache_path)
        
    # 3. Remove from registry
    module_repository.remove_module(base_dir, name)

def update_modules(root_dir: Path, global_scope: bool = False):
    base_dir = get_global_rune_dir() if global_scope else root_dir
    modules = module_repository.list_modules(base_dir)
    agents = config_repository.get_agent_names(base_dir)
    for mod in modules:
        add_module(root_dir, mod.url, mod.path, mod.name, mod.type, agents, global_scope)
