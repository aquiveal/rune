# Changelog v0.1.0

## Breaking Changes

*   **Module Management Architecture Migration**
    Migrated from git submodules to a service-oriented architecture utilizing Pydantic schemas, sparse checkout, and direct git cloning.
    *   **Migration Path:** Existing git submodules must be removed from your repository. The system now handles module fetching dynamically; ensure your environment has git access and Pydantic installed.
    *   **Commits:** [167](https://github.com/aquiveal/rune/commit/167), [168](https://github.com/aquiveal/rune/commit/168), [217](https://github.com/aquiveal/rune/commit/217)

*   **CLI Command Structure Refactor**
    Refactored the CLI to utilize dedicated sub-apps (skills, rules, modules) and removed the legacy `develop` command.
    *   **Migration Path:** Update all scripts and CI/CD pipelines to use the new sub-app commands (e.g., `cli modules ...`) instead of the removed `develop` command.
    *   **Commits:** [214](https://github.com/aquiveal/rune/commit/214), [215](https://github.com/aquiveal/rune/commit/215), [254](https://github.com/aquiveal/rune/commit/254)

## New Features

*   **Automated Rule and Skill Documentation**
    Implemented automated merging of rules into `AGENTS.md` and continuous updates to `SKILL.md` documentation.
    *   **Commits:** [175](https://github.com/aquiveal/rune/commit/175), [230](https://github.com/aquiveal/rune/commit/230), [231](https://github.com/aquiveal/rune/commit/231)

## Infrastructure

*   **Centralized Configuration Management**
    Centralized `bumpver` configuration to the root directory and migrated settings to Pydantic models to support environment-aware configuration.
    *   **Commits:** [29](https://github.com/aquiveal/rune/commit/29), [35](https://github.com/aquiveal/rune/commit/35), [248](https://github.com/aquiveal/rune/commit/248)

## Documentation

*   **Architectural Standards Documentation**
    Added comprehensive documentation covering Python development standards, Clean Architecture, and domain-driven design principles.
    *   **Commits:** [40](https://github.com/aquiveal/rune/commit/40), [41](https://github.com/aquiveal/rune/commit/41), [222](https://github.com/aquiveal/rune/commit/222)
