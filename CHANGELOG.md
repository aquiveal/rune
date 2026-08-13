## Breaking Changes

- **MCP Setup Configuration Update**
  Added `skip_if_global` parameter to the MCP server configuration function and tests to prevent duplicate workspace configurations.
  Commits: [c074e6e](https://github.com/aquiveal/rune/commit/c074e6e6), [937405a](https://github.com/aquiveal/rune/commit/937405a0), [4b13684](https://github.com/aquiveal/rune/commit/4b13684a)

- **API and URL Detection Changes**
  Added the `skip_if_global` parameter to MCP setup configuration and refactored URL detection utilities (`is_git_source` to `is_git`, `is_web_url` to `is_site`), which may affect existing programmatic integrations.
  Migration: Update any calls to the MCP setup configuration to handle the new parameter and update references of old URL detection utility names to their new equivalents.

## Improvements

- **URL Detection Utilities Refactor**
  Reorganized imports and refactored URL detection utilities, renaming `is_git_source` to `is_git` and `is_web_url` to `is_site` (with aliases), and added `KNOWN_GIT_HOSTS`.
  Commits: [f175b19](https://github.com/aquiveal/rune/commit/f175b199), [596b9c1](https://github.com/aquiveal/rune/commit/596b9c17)
