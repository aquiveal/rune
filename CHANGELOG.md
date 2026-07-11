# Changelog v2.1.4

## Improvements

* **Logging Framework Migration**
  Replaced the internal `worldline` logging dependency with `structlog` to improve structured logging capabilities and updated associated configuration settings.
  Commits: [181f3f0](https://github.com/aquiveal/rune/commit/181f3f08), [4859755](https://github.com/aquiveal/rune/commit/4859755f)

* **Workspace Agent Resolution Logic**
  Simplified the agent resolution process by removing interactive CLI prompts and defaulting exclusively to the `.agents` configuration file.
  Commits: [181f3f0](https://github.com/aquiveal/rune/commit/181f3f08), [4859755](https://github.com/aquiveal/rune/commit/4859755f)
