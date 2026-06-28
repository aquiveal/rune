# Changelog v2.0.0

## Breaking Changes

* **Namespace Migration: Rename Lume to Worldline**
  All references, dependencies, imports, and configurations previously namespaced under `lume` have been renamed to `worldline`. This is a high-severity breaking change requiring updates to all project configuration files, import statements, and dependency references.
  * Migration: Update your codebase to replace all instances of `lume` with `worldline`. Ensure local environment variables and build scripts are updated to reflect the new namespace.
  * Commits: [51acc1b](https://github.com/aquiveal/rune/commit/51acc1bf), [c92e5a5](https://github.com/aquiveal/rune/commit/c92e5a5b)

## New Features

* **Automated Skill Tree Scaffolding**
  The `update_skill_tree` function now includes logic to automatically scaffold the necessary directory structure, including `scripts`, `references`, `assets`, and `modules`, as well as generating or updating the `SKILL.md` file.
  * Commits: [51acc1b](https://github.com/aquiveal/rune/commit/51acc1bf), [c92e5a5](https://github.com/aquiveal/rune/commit/c92e5a5b)
