import os
from pathlib import Path
from typing import List
from rune.config.main import RUNE_DIR, RUNE_MODULES_DIR, RUNE_MODULES_FILE, RUNE_CONFIG, RUNE_INDEX, DEFAULT_AGENTS, get_global_rune_dir
from rune.repositories import config_repository

def is_initialized(root_dir: Path) -> bool:
    return (root_dir / RUNE_DIR).is_dir()

def init_workspace(root_dir: Path):
    rune_dir = root_dir / RUNE_DIR
    (rune_dir / RUNE_MODULES_DIR).mkdir(parents=True, exist_ok=True)
    (root_dir / RUNE_MODULES_FILE).touch(exist_ok=True)
    (rune_dir / RUNE_CONFIG).touch(exist_ok=True)
    (rune_dir / RUNE_INDEX).touch(exist_ok=True)
    update_gitignore(root_dir)

def detect_agents(root_dir: Path) -> List[str]:
    detected = []
    # Check for directories in root
    for agent in DEFAULT_AGENTS:
        if (root_dir / agent).is_dir():
            detected.append(agent)
    
    # Also check config
    config_agents = config_repository.get_agent_names(root_dir)
    for a in config_agents:
        if a not in detected:
            detected.append(a)
            
    return detected

def update_gitignore(root_dir: Path):
    gitignore_file = root_dir / ".gitignore"
    content = gitignore_file.read_text() if gitignore_file.exists() else ""
    lines = content.splitlines()
    
    entries = [f"{RUNE_DIR}/"]
    agents = config_repository.get_agent_names(root_dir)
    for agent in agents:
        entries.append(f"{agent}/")
        
    missing = [e for e in entries if e not in lines and e.strip('/') not in lines]
    
    if missing:
        if content and not content.endswith("\n"):
            content += "\n"
        if "# Rune" not in lines:
            content += "\n# Rune\n"
        for e in missing:
            content += f"{e}\n"
        gitignore_file.write_text(content)
