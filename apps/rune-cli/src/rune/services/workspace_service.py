from pathlib import Path
from typing import List, Optional

import questionary

from rune.config.main import settings
from rune.repositories import config_repository


def is_initialized(root_dir: Path) -> bool:
    return (root_dir / ".rune").is_dir()


def init_workspace(root_dir: Path):
    rune_dir = root_dir / ".rune"
    (rune_dir / "modules").mkdir(parents=True, exist_ok=True)
    (root_dir / ".runemodules").touch(exist_ok=True)
    (rune_dir / "config").touch(exist_ok=True)
    (rune_dir / "index").touch(exist_ok=True)
    update_gitignore(root_dir)


def detect_agents(root_dir: Path) -> List[str]:
    if settings.agent.names:
        return [settings.agent.names[0]]

    for agent in settings.agents:
        if (root_dir / agent).is_dir():
            return [agent]

    return []


def resolve_target_agents(
    git_root: Optional[Path],
    cwd: Path,
    global_scope: bool,
    agents_arg: Optional[List[str]],
) -> Optional[List[str]]:
    target_agents = []
    if global_scope or cwd == git_root:
        target_agents = agents_arg or detect_agents(git_root or cwd)
        if not target_agents and not agents_arg:
            target_agents = [".agents"]
            config_repository.add_agent_name(git_root or cwd, ".agents")

        if target_agents is not None and ".agents" not in target_agents:
            target_agents.append(".agents")

    return target_agents


def update_gitignore(root_dir: Path):
    gitignore_file = root_dir / ".gitignore"
    content = gitignore_file.read_text() if gitignore_file.exists() else ""
    lines = content.splitlines()

    # Remove old .rune/ entry if it exists
    if ".rune/" in lines:
        lines.remove(".rune/")
        content = "\n".join(lines)
        if content and not content.endswith("\n"):
            content += "\n"

    entries = [
        ".rune/*",
        "!.rune/config",
        "!.rune/index",
    ]

    missing = [e for e in entries if e not in lines and e.strip("/") not in lines]

    if missing:
        if content and not content.endswith("\n"):
            content += "\n"
        if "# Rune" not in lines:
            content += "\n# Rune\n"
        for e in missing:
            content += f"{e}\n"
        gitignore_file.write_text(content)
