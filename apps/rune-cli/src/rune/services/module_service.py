import shutil
import os
from pathlib import Path
from typing import List, Optional, Dict
from rune.config.exceptions import ModuleError
from rune.repositories import git_repository, module_repository
from rune.schemas.module_schema import ModuleSchema


def add_module(
    git_root: Path,
    cwd: Path,
    url: str,
    path: str,
    name: str,
    type: str,
    agents: List[str],
    global_scope: bool = False,
    copy_mode: bool = False,
):
    base_dir = (Path.home() / ".rune") if global_scope else git_root
    rune_dir = base_dir / ".rune"

    repo_name = url.rstrip("/").split("/")[-1].replace(".git", "")
    cache_path = rune_dir / "modules" / type / repo_name

    # Always use git clone for modules tracked in .runemodules
    if not cache_path.exists():
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        git_repository.clone(url, cache_path)
        if path and path != ".":
            git_repository.sparse_checkout_init(cache_path)
            git_repository.sparse_checkout_set(cache_path, [path])
    else:
        if path and path != ".":
            git_repository.sparse_checkout_init(cache_path)
            git_repository.sparse_checkout_add(cache_path, [path])

    source_path = cache_path / path
    if not source_path.exists():
        raise ModuleError(f"Path '{path}' not found in repository")

    # Deploy to agents or cwd
    target_paths = []
    if global_scope or cwd == git_root:
        for agent in agents:
            target_paths.append(base_dir / agent / type / name)
    else:
        if cwd.name == type:
            target_paths.append(cwd / name)
        else:
            target_paths.append(cwd / type / name)

    default_branch = git_repository.get_default_branch(url)
    specific_url = (
        f"{url.rstrip('.git')}/tree/{default_branch}/{path}"
        if path and path != "."
        else f"{url.rstrip('.git')}/tree/{default_branch}"
    )

    for agent_path in target_paths:
        agent_path.parent.mkdir(parents=True, exist_ok=True)

        def on_rm_error(func, path, exc_info):
            import stat

            os.chmod(path, stat.S_IWRITE)
            func(path)

        if agent_path.exists():
            if agent_path.is_symlink():
                agent_path.unlink(missing_ok=True)
            elif agent_path.is_dir():
                shutil.rmtree(agent_path, onerror=on_rm_error)
            else:
                agent_path.unlink(missing_ok=True)

        # Always copy instead of symlink to avoid cross-OS issues (Windows + WSL)
        if source_path.is_dir():
            shutil.copytree(
                source_path,
                agent_path,
                dirs_exist_ok=True,
                ignore_dangling_symlinks=True,
            )

            # Remove .git if it was copied (e.g. submodule fetching)
            git_dir = agent_path / ".git"
            try:
                if git_dir.exists():
                    shutil.rmtree(git_dir, ignore_errors=True)
            except Exception:
                pass
        else:
            shutil.copy2(source_path, agent_path)

        # Update registry for each target path
        rel_path = str(agent_path.relative_to(base_dir)).replace("\\", "/")
        module_repository.add_module(
            base_dir, ModuleSchema(name=rel_path, url=specific_url, path=rel_path)
        )

        # Add to .gitignore if not already there
        gitignore_path = base_dir / ".gitignore"
        if gitignore_path.exists():
            content = gitignore_path.read_text()
            if rel_path not in content:
                with open(gitignore_path, "a") as f:
                    if not content.endswith("\n"):
                        f.write("\n")
                    f.write(f"{rel_path}\n")

        # Generate repomap for modules (submodules)
        if type == "modules" and agent_path.is_dir():
            from rune.services import map_service

            try:
                # Generate map using source_path (which has .git) so Aider tracks files properly
                map_text = map_service.generate_submodule_map(source_path)
                (agent_path / ".repomap.txt").write_text(map_text, encoding="utf-8")
            except Exception as e:
                import sys

                print(
                    f"Warning: Failed to generate repomap for {agent_path.name}: {e}",
                    file=sys.stderr,
                )


def get_status(git_root: Path, global_scope: bool = False) -> Dict[str, str]:
    base_dir = (Path.home() / ".rune") if global_scope else git_root
    modules = module_repository.list_modules(base_dir)

    status = {}
    for mod in modules:
        mod_status = "OK"
        repo_name = mod.base_url.rstrip("/").split("/")[-1].replace(".git", "")
        cache_path = (
            base_dir
            / ".rune"
            / "modules"
            / mod.inferred_type
            / repo_name
            / mod.source_path
        )
        if not cache_path.exists():
            mod_status = "Missing Cache"
        else:
            agent_path = base_dir / mod.path
            if not agent_path.exists():
                mod_status = "Missing"
        status[mod.path] = mod_status
    return status


def remove_module(git_root: Path, name: str, type: str, global_scope: bool = False):
    base_dir = (Path.home() / ".rune") if global_scope else git_root

    # If name is not a path, we need to find the matching paths
    modules = module_repository.list_modules(base_dir)
    to_remove = []
    for mod in modules:
        if mod.path == name or mod.path.endswith(f"/{type}/{name}"):
            to_remove.append(mod)

    for mod in to_remove:
        agent_path = base_dir / mod.path
        if agent_path.exists():
            if agent_path.is_symlink():
                agent_path.unlink(missing_ok=True)
            else:
                shutil.rmtree(agent_path)
        module_repository.remove_module(base_dir, mod.name)


def update_modules(
    git_root: Path, type: Optional[str] = None, global_scope: bool = False
):
    base_dir = (Path.home() / ".rune") if global_scope else git_root
    modules = module_repository.list_modules(base_dir)

    if type:
        modules = [m for m in modules if m.inferred_type == type]

    updated_repos = set()

    for mod in modules:
        repo_name = mod.base_url.rstrip("/").split("/")[-1].replace(".git", "")
        cache_path = base_dir / ".rune" / "modules" / mod.inferred_type / repo_name

        if cache_path not in updated_repos:
            if cache_path.exists():
                git_repository.run_git(["pull"], cwd=cache_path)
                if mod.source_path and mod.source_path != ".":
                    git_repository.sparse_checkout_init(cache_path)
                    git_repository.sparse_checkout_add(cache_path, [mod.source_path])
            else:
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                git_repository.clone(mod.base_url, cache_path)
                if mod.source_path and mod.source_path != ".":
                    git_repository.sparse_checkout_init(cache_path)
                    git_repository.sparse_checkout_set(cache_path, [mod.source_path])
            updated_repos.add(cache_path)

        source_path = cache_path / mod.source_path
        if source_path.exists():
            agent_path = base_dir / mod.path
            if not agent_path.exists():
                agent_path.parent.mkdir(parents=True, exist_ok=True)

            def on_rm_error(func, path, exc_info):
                import stat

                os.chmod(path, stat.S_IWRITE)
                func(path)

            if agent_path.exists():
                if agent_path.is_symlink():
                    agent_path.unlink(missing_ok=True)
                elif agent_path.is_dir():
                    shutil.rmtree(agent_path, onerror=on_rm_error)
                else:
                    agent_path.unlink(missing_ok=True)

            if source_path.is_dir():
                shutil.copytree(
                    source_path,
                    agent_path,
                    dirs_exist_ok=True,
                    ignore_dangling_symlinks=True,
                )
                git_dir = agent_path / ".git"
                try:
                    if git_dir.exists():
                        shutil.rmtree(git_dir, ignore_errors=True)
                except Exception:
                    pass

                if mod.inferred_type == "modules":
                    from rune.services import map_service

                    try:
                        # Generate map using source_path (which has .git) so Aider tracks files properly
                        map_text = map_service.generate_submodule_map(source_path)
                        (agent_path / ".repomap.txt").write_text(
                            map_text, encoding="utf-8"
                        )
                    except Exception as e:
                        import sys

                        print(
                            f"Warning: Failed to generate repomap for {agent_path.name}: {e}",
                            file=sys.stderr,
                        )
            else:
                shutil.copy2(source_path, agent_path)
