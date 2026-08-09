"""Service package for Rune CLI."""

from rune.services import (
    map_service,
    mcp_service,
    module_service,
    mutagen_service,
    rule_service,
    skill_service,
    submodule_service,
    workspace_service,
)
from rune.services.map_service import (
    generate_submodule_map,
    merge_ast_to_agents_md,
)
from rune.services.mcp_service import (
    add_mcp_server,
    discover_mcp_servers_in_repo,
    get_builtin_registry,
    list_mcp_servers,
    remove_mcp_server,
    search_registry,
    validate_mcp_file,
)
from rune.services.module_service import (
    add_module,
    get_status,
    remove_module,
    update_modules,
)
from rune.services.mutagen_service import (
    parse_gitignore,
    update_mutagen_ignore,
)
from rune.services.rule_service import (
    discover_rule_dirs,
    discover_rules,
    merge_rules_to_agents_md,
    validate_rule_file,
)
from rune.services.skill_service import (
    discover_skills,
    ensure_skill_md,
    generate_tree,
    sanitize_skill_name,
    update_skill_instructions,
    validate_skill_file,
)
from rune.services.submodule_service import (
    detect_potential_submodules,
    get_configured_submodules,
    merge_submodules_upward_to_workspace,
    prompt_and_configure_submodules,
    propagate_workspace_to_submodule,
    update_all_submodules,
)
from rune.services.workspace_service import (
    detect_agents,
    init_workspace,
    is_initialized,
    resolve_target_agents,
    update_gitignore,
)

__all__ = [
    "add_mcp_server",
    "add_module",
    "detect_agents",
    "detect_potential_submodules",
    "discover_mcp_servers_in_repo",
    "discover_rule_dirs",
    "discover_rules",
    "discover_skills",
    "ensure_skill_md",
    "generate_submodule_map",
    "generate_tree",
    "get_builtin_registry",
    "get_configured_submodules",
    "get_status",
    "init_workspace",
    "is_initialized",
    "list_mcp_servers",
    "map_service",
    "mcp_service",
    "merge_ast_to_agents_md",
    "merge_rules_to_agents_md",
    "merge_submodules_upward_to_workspace",
    "module_service",
    "mutagen_service",
    "parse_gitignore",
    "prompt_and_configure_submodules",
    "propagate_workspace_to_submodule",
    "remove_mcp_server",
    "remove_module",
    "resolve_target_agents",
    "rule_service",
    "sanitize_skill_name",
    "search_registry",
    "skill_service",
    "submodule_service",
    "update_all_submodules",
    "update_gitignore",
    "update_modules",
    "update_mutagen_ignore",
    "update_skill_instructions",
    "validate_mcp_file",
    "validate_rule_file",
    "validate_skill_file",
    "workspace_service",
]
