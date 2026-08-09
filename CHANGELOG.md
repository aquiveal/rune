# Changelog v2.3.0

## New Features

* **Crawl4AI Integration**: Added support for the Crawl4AI open-source web crawler as an MCP server with Docker container management, API token prompting, and comprehensive tests ([3d7c94e](https://github.com/aquiveal/rune/commit/3d7c94e0), [5043574](https://github.com/aquiveal/rune/commit/50435741), [c66528a](https://github.com/aquiveal/rune/commit/c66528a6)).

## Improvements

* **Crawl4AI Configuration**: Added `CRAWL4AI_API_KEY` and `CRAWL4AI_API_TOKEN` environment variables to the Crawl4AI MCP server configuration ([c9fbe2a](https://github.com/aquiveal/rune/commit/c9fbe2a4)).

## Infrastructure

* **Architecture Rules Clean Up**: Removed redundant architecture documentation files and consolidated rule directories ([aef3272](https://github.com/aquiveal/rune/commit/aef3272f)).
* **Release Workflow Update**: Updated GitHub Actions workflow organization name and renamed the workflow to Tag & Release ([5abcee6](https://github.com/aquiveal/rune/commit/5abcee68)).
* **Versioning Tool Migration**: Replaced `bumpver` with `bumpversion` in a dedicated configuration file for better compatibility ([49bb19c](https://github.com/aquiveal/rune/commit/49bb19c0)).

## Docs

* **PR Template Cleanup**: Removed the redundant developer checklist section from the pull request template ([e3c722f](https://github.com/aquiveal/rune/commit/e3c722f3)).

## Other

* **MCP Registry Extraction**: Extracted MCP registry definitions into separate modules and updated the workspace service to use workspace-scoped MCP installation ([c7d16ab](https://github.com/aquiveal/rune/commit/c7d16abf), [81878b4](https://github.com/aquiveal/rune/commit/81878b41), [42333f0](https://github.com/aquiveal/rune/commit/42333f08)).
