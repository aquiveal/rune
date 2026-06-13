import subprocess
from pathlib import Path
from typing import List, Optional
from rune.config.exceptions import GitError

def run_git(args: List[str], cwd: Optional[Path] = None, capture_output: bool = True) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            ["git"] + args,
            cwd=str(cwd) if cwd else None,
            capture_output=capture_output,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise GitError(f"Git command failed: {' '.join(e.cmd)}\nError: {e.stderr}")

def clone(url: str, target_path: Path, depth: Optional[int] = None):
    args = ["clone"]
    if depth:
        args += ["--depth", str(depth)]
    args += [url, str(target_path)]
    run_git(args)

def add_submodule(url: str, path: str, cwd: Path):
    run_git(["-c", "protocol.file.allow=always", "submodule", "add", url, path], cwd=cwd)

def update_submodules(cwd: Path, init: bool = True, recursive: bool = True):
    args = ["submodule", "update"]
    if init:
        args.append("--init")
    if recursive:
        args.append("--recursive")
    run_git(args, cwd=cwd)

def get_config(key: str, file_path: Path) -> Optional[str]:
    try:
        result = run_git(["config", "--file", str(file_path), key])
        return result.stdout.strip()
    except GitError:
        return None

def get_config_all(key: str, file_path: Path) -> List[str]:
    try:
        result = run_git(["config", "--file", str(file_path), "--get-all", key])
        return [line for line in result.stdout.strip().split("\n") if line]
    except GitError:
        return []

def set_config(key: str, value: str, file_path: Path):
    run_git(["config", "--file", str(file_path), key, value])

def add_config(key: str, value: str, file_path: Path):
    run_git(["config", "--file", str(file_path), "--add", key, value])

def unset_config_section(section: str, file_path: Path):
    try:
        run_git(["config", "--file", str(file_path), "--remove-section", section])
    except GitError:
        pass # Section might not exist
