# Changelog v1.0.0

## Breaking Changes

*   **Configuration Management: Migration to Pydantic Settings**
    Replaced static configuration variables with a centralized Pydantic Settings class for environment variable injection.
    *   **Migration:** Update all environment variables to match the new Pydantic schema; static configuration files must be migrated to the new Settings class structure.
    *   **Commits:** [174](https://github.com/aquiveal/rune/commit/174), [40](https://github.com/aquiveal/rune/commit/40), [34](https://github.com/aquiveal/rune/commit/34)

*   **Dependency Management: Removal of Git Submodules**
    Removed git submodules in favor of direct git clone and sparse checkout workflows.
    *   **Migration:** Remove existing git submodules from your local repository using `git submodule deinit .` and re-initialize the project environment to use the new sparse checkout workflow.
    *   **Commits:** [172](https://github.com/aquiveal/rune/commit/172), [222](https://github.com/aquiveal/rune/commit/222), [233](https://github.com/aquiveal/rune/commit/233)

## Features

*   **CLI Integration: Aider-chat and Repomap Support**
    Added dependencies for `aider-chat` and implemented repomap generation to enable context-aware operations within the CLI.
    *   **Commits:** [95](https://github.com/aquiveal/rune/commit/95), [96](https://github.com/aquiveal/rune/commit/96), [98](https://github.com/aquiveal/rune/commit/98)

## Docs

*   **Architectural Standards Documentation**
    Added comprehensive documentation covering Python development standards and domain-driven design (DDD) principles.
    *   **Commits:** [45](https://github.com/aquiveal/rune/commit/45), [46](https://github.com/aquiveal/rune/commit/46), [227](https://github.com/aquiveal/rune/commit/227)

*   **Pull Request Template Cleanup**
    Refined the pull request template by removing redundant system instructions to streamline the contribution process.
    *   **Commits:** [186](https://github.com/aquiveal/rune/commit/186), [188](https://github.com/aquiveal/rune/commit/188), [190](https://github.com/aquiveal/rune/commit/190)

## Other

*   **Project Versioning**
    Finalized project versioning set to 26.6.40.
    *   **Commits:** [41](https://github.com/aquiveal/rune/commit/41)
