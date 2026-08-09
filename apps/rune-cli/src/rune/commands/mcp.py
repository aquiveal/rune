import json
from pathlib import Path
from typing import Annotated

import questionary
import structlog
import typer

from rune.config.exceptions import RuneError, ValidationError
from rune.repositories import git_repository
from rune.schemas.mcp_schema import (
    McpServerUnion,
    McpSettings,
    McpSseServer,
    McpStdioServer,
    McpStreamableHttpServer,
)
from rune.services import mcp_service

__all__ = []

app = typer.Typer(
    no_args_is_help=True, help="Manage Model Context Protocol (MCP) servers and tools"
)
logger = structlog.get_logger(__name__)


def _parse_env_list(env_list: list[str] | None) -> dict[str, str] | None:
    if not env_list:
        return None
    env_dict = {}
    for item in env_list:
        if "=" in item:
            k, v = item.split("=", 1)
            env_dict[k.strip()] = v.strip()
        else:
            env_dict[item.strip()] = ""
    return env_dict


@app.command("add")
def add(
    source: Annotated[
        str,
        typer.Argument(
            help="Registry key (e.g. probelabs/probe), Git owner/repo, URL, or local file"
        ),
    ],
    global_scope: Annotated[
        bool,
        typer.Option("--global", "-g", help="Install globally across agent settings"),
    ] = False,
    agents: Annotated[
        list[str] | None,
        typer.Option("--agent", "-a", help="Target agents"),
    ] = None,
    transport: Annotated[
        str | None,
        typer.Option(
            "--transport", "-t", help="Transport type: stdio, sse, streamable-http"
        ),
    ] = None,
    command: Annotated[
        str | None,
        typer.Option("--command", "-c", help="Command executable for stdio transport"),
    ] = None,
    args: Annotated[
        list[str] | None,
        typer.Option("--arg", help="Arguments for stdio command"),
    ] = None,
    env: Annotated[
        list[str] | None,
        typer.Option("--env", help="Environment variables as KEY=VALUE"),
    ] = None,
    url: Annotated[
        str | None,
        typer.Option("--url", help="Endpoint URL for sse or streamable-http transport"),
    ] = None,
    disabled: Annotated[
        bool,
        typer.Option("--disabled", help="Add server in disabled state"),
    ] = False,
    timeout: Annotated[
        int,
        typer.Option("--timeout", help="Server timeout in seconds"),
    ] = 60,
    always_allow: Annotated[
        list[str] | None,
        typer.Option("--always-allow", help="Auto-approved tool names"),
    ] = None,
):
    """Add or install an MCP server configuration."""
    cwd = Path.cwd()
    git_root = git_repository.get_git_root(cwd)

    if not global_scope and not git_root:
        msg = "Must be run inside a git repository or with --global (-g)."
        logger.error(msg)
        typer.echo(msg, err=True)
        raise typer.Exit(1)

    custom_config: McpServerUnion | None = None
    if transport or command or url:
        env_dict = _parse_env_list(env)
        transport_type = (transport or ("stdio" if command else "sse")).lower()

        if transport_type == "stdio":
            if not command:
                msg = "--command (-c) is required for stdio transport."
                logger.error(msg)
                typer.echo(msg, err=True)
                raise typer.Exit(1)
            custom_config = McpStdioServer(
                type="stdio",
                command=command,
                args=args,
                env=env_dict,
                disabled=disabled,
                timeout=timeout,
                alwaysAllow=always_allow,
            )
        elif transport_type == "sse":
            if not url:
                msg = "--url is required for sse transport."
                logger.error(msg)
                typer.echo(msg, err=True)
                raise typer.Exit(1)
            custom_config = McpSseServer(
                type="sse",
                url=url,
                disabled=disabled,
                timeout=timeout,
                alwaysAllow=always_allow,
            )
        elif transport_type == "streamable-http":
            if not url:
                msg = "--url is required for streamable-http transport."
                logger.error(msg)
                typer.echo(msg, err=True)
                raise typer.Exit(1)
            custom_config = McpStreamableHttpServer(
                type="streamable-http",
                url=url,
                disabled=disabled,
                timeout=timeout,
                alwaysAllow=always_allow,
            )
        else:
            msg = f"Unsupported transport type '{transport_type}'. Must be stdio, sse, or streamable-http."
            logger.error(msg)
            typer.echo(msg, err=True)
            raise typer.Exit(1)

    try:
        updated_paths = mcp_service.add_mcp_server(
            source=source,
            git_root=git_root,
            cwd=cwd,
            global_scope=global_scope,
            agent_override=agents,
            custom_config=custom_config,
        )
        if updated_paths:
            scope_str = "globally" if global_scope else "in workspace"
            msg = f"Successfully added MCP server '{source}' {scope_str} across configurations:"
            logger.info(msg)
            typer.echo(msg)
            for p in updated_paths:
                p_msg = f"  - {p}"
                logger.info(p_msg)
                typer.echo(p_msg)
        else:
            msg = "No configuration files were modified."
            logger.warning(msg)
            typer.echo(msg)

    except RuneError as e:
        logger.error(str(e))
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
    except Exception as e:  # noqa: BLE001
        msg = f"Unexpected error adding MCP server: {e}"
        logger.error(msg)
        typer.echo(msg, err=True)
        raise typer.Exit(1)


@app.command("list")
def list_servers(
    global_scope: Annotated[
        bool,
        typer.Option("--global", "-g", help="List global MCP servers"),
    ] = False,
):
    """List configured MCP servers."""
    cwd = Path.cwd()
    git_root = git_repository.get_git_root(cwd) or cwd
    base_dir = (Path.home() / ".rune") if global_scope else git_root

    servers = mcp_service.list_mcp_servers(base_dir, global_scope=global_scope)
    if not servers:
        scope_str = "global" if global_scope else "workspace"
        msg = f"No MCP servers configured in {scope_str} scope."
        logger.info(msg)
        typer.echo(msg)
        return

    hdr = f"Configured MCP Servers ({'global' if global_scope else 'workspace'} scope):"
    logger.info(hdr)
    typer.echo(hdr)
    for s_name, info in servers.items():
        cfg = info.get("config", {})
        agents_str = ", ".join(info.get("agents", []))
        t_type = cfg.get("type", "stdio")
        cmd_or_url = cfg.get("command") or cfg.get("url") or "n/a"
        dis_str = " [DISABLED]" if cfg.get("disabled") else ""
        item_msg = (
            f"  - {s_name}{dis_str} ({t_type}: {cmd_or_url}) -> Agents: [{agents_str}]"
        )
        logger.info(item_msg)
        typer.echo(item_msg)


@app.command("remove")
def remove(
    names: Annotated[
        list[str],
        typer.Argument(help="Names of MCP servers to remove"),
    ],
    global_scope: Annotated[
        bool,
        typer.Option("--global", "-g", help="Remove from global scope"),
    ] = False,
):
    """Remove MCP server configurations."""
    cwd = Path.cwd()
    git_root = git_repository.get_git_root(cwd) or cwd
    base_dir = (Path.home() / ".rune") if global_scope else git_root

    modified = mcp_service.remove_mcp_server(names, base_dir, global_scope=global_scope)
    if modified:
        msg = f"Removed server(s) {', '.join(names)} from configuration files:"
        logger.info(msg)
        typer.echo(msg)
        for p in modified:
            p_msg = f"  - {p}"
            logger.info(p_msg)
            typer.echo(p_msg)
    else:
        msg = f"No servers found matching: {', '.join(names)}"
        logger.warning(msg)
        typer.echo(msg)


@app.command("init")
def init(
    name: Annotated[
        str,
        typer.Argument(help="Name of the MCP server"),
    ] = "custom-mcp",
):
    """Scaffold a new mcp.json file interactively."""
    cwd = Path.cwd()
    target_file = cwd / "mcp.json"

    transport = questionary.select(
        "Select transport type:",
        choices=["stdio", "sse", "streamable-http"],
    ).ask()

    if not transport:
        return

    if transport == "stdio":
        cmd = questionary.text(
            "Enter command executable (e.g. node, npx, python):", default="npx"
        ).ask()
        args_str = questionary.text(
            "Enter command arguments (space separated):", default=""
        ).ask()
        args = args_str.split() if args_str else []

        server_cfg = McpStdioServer(
            type="stdio",
            command=cmd,
            args=args,
        )
    elif transport == "sse":
        endpoint_url = questionary.text("Enter SSE endpoint URL:").ask()
        server_cfg = McpSseServer(
            type="sse",
            url=endpoint_url,
        )
    else:
        endpoint_url = questionary.text("Enter streamable-http endpoint URL:").ask()
        server_cfg = McpStreamableHttpServer(
            type="streamable-http",
            url=endpoint_url,
        )

    settings = McpSettings(mcpServers={name: server_cfg})
    target_file.write_text(
        json.dumps(settings.model_dump(exclude_none=True, mode="json"), indent=2),
        encoding="utf-8",
    )
    msg = f"Scaffolded MCP configuration at {target_file}"
    logger.info(msg)
    typer.echo(msg)


@app.command("update")
def update(
    global_scope: Annotated[
        bool,
        typer.Option("--global", "-g", help="Update global MCP configurations"),
    ] = False,
):
    """Sync and validate MCP configurations across agents."""
    cwd = Path.cwd()
    git_root = git_repository.get_git_root(cwd) or cwd
    base_dir = (Path.home() / ".rune") if global_scope else git_root

    servers = mcp_service.list_mcp_servers(base_dir, global_scope=global_scope)
    msg = f"Validated and synchronized {len(servers)} MCP server configuration(s)."
    logger.info(msg)
    typer.echo(msg)


@app.command("validate")
def validate(
    path: Annotated[
        Path | None,
        typer.Argument(help="Path to mcp.json file to validate"),
    ] = None,
):
    """Validate an mcp.json file against the MCP specification."""
    target_path = path or (Path.cwd() / "mcp.json")
    try:
        settings = mcp_service.validate_mcp_file(target_path)
        count = len(settings.mcpServers)
        msg = f"Configuration file '{target_path}' is valid! Contains {count} server definition(s)."
        logger.info(msg)
        typer.echo(msg)
    except ValidationError as e:
        msg = f"Validation failed for '{target_path}': {e}"
        logger.error(msg)
        typer.echo(msg, err=True)
        raise typer.Exit(1)
    except Exception as e:  # noqa: BLE001
        msg = f"An unexpected error occurred: {e}"
        logger.error(msg)
        typer.echo(msg, err=True)
        raise typer.Exit(1)


@app.command("registry")
def registry_cmd(
    query: Annotated[
        str | None,
        typer.Argument(help="Search term for MCP registry"),
    ] = None,
):
    """Search or list built-in MCP server registry entries."""
    if query:
        entries = mcp_service.search_registry(query)
    else:
        entries = list(mcp_service.get_builtin_registry().values())

    if not entries:
        msg = "No matching MCP registry entries found."
        logger.info(msg)
        typer.echo(msg)
        return

    hdr = "MCP Server Registry Entries:"
    logger.info(hdr)
    typer.echo(hdr)
    seen = set()
    for entry in entries:
        if entry.name in seen:
            continue
        seen.add(entry.name)
        pkg_str = f" ({entry.package})" if entry.package else ""
        item_msg = f"  - {entry.name}{pkg_str}\n    Description: {entry.description}"
        if entry.repository:
            item_msg += f"\n    Repository: {entry.repository}"
        logger.info(item_msg)
        typer.echo(item_msg)
