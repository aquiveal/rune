# Changelog v2.1.0

## Features

* **Agents CLI Command Group**
  Introduced the `agents` command group to the CLI, enabling programmatic management of agent configurations. This includes the `update` command for managing contexts, rules, and skills.
  Commits: [1d8bc1d](https://github.com/aquiveal/rune/commit/1d8bc1d7), [aac81f2](https://github.com/aquiveal/rune/commit/aac81f28), [16d6653](https://github.com/aquiveal/rune/commit/16d66530)

* **Repository AST Map Generation**
  Added functionality within the `agents update` command to generate repository AST maps, featuring native `.gitignore` support to ensure accurate indexing of project structures.
  Commits: [1d8bc1d](https://github.com/aquiveal/rune/commit/1d8bc1d7), [aac81f2](https://github.com/aquiveal/rune/commit/aac81f28), [16d6653](https://github.com/aquiveal/rune/commit/16d66530)

## Docs

* **Agents Command Documentation**
  Updated the README to include comprehensive usage instructions and configuration examples for the new `agents` CLI command group.
  Commit: [037a9b5](https://github.com/aquiveal/rune/commit/037a9b51)

## Other

* **Test Coverage Expansion**
  Added comprehensive unit tests for the map service and the `agents update` command to ensure stability of the new CLI features.
  Commits: [ebf8fd5](https://github.com/aquiveal/rune/commit/ebf8fd5a), [2bfd7e1](https://github.com/aquiveal/rune/commit/2bfd7e1b)

* **Dependency Updates**
  Updated `worldline` to version 2.0.1.
  Commit: [37f2b04](https://github.com/aquiveal/rune/commit/37f2b04b)

* **Dependency Downgrades**
  Downgraded `posthog` to version 7.8.6 to resolve compatibility issues.
  Commit: [37f2b04](https://github.com/aquiveal/rune/commit/37f2b04b)
