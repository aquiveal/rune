# Changelog

All notable changes to this project will be documented in this file.

## [26.6.15] - 2026-06-13

### 🚜 Refactor

- Update rules block injection in AGENTS.md
- Update regex to only match # Rules block
- Improve rule content formatting

## [26.6.14] - 2026-06-13

### 🚀 Features

- Add helper properties to module schema

### 🐛 Bug Fixes

- Update module filtering logic
- Quote module names and add branch detection

### 🚜 Refactor

- Simplify module management and cache logic
- Replace git submodules with clone logic

### ⚙️ Miscellaneous Tasks

- Release 26.6.14

## [26.6.13] - 2026-06-13

### 🚀 Features

- Auto-merge rules into AGENTS.md after install

### 🐛 Bug Fixes

- Replace symlinks with hard copies

### 🧪 Testing

- Update module service test mocks

### ⚙️ Miscellaneous Tasks

- Release 26.6.13

## [26.6.12] - 2026-06-13

### 🚀 Features

- Discover rule directories in rules folder

### ⚙️ Miscellaneous Tasks

- Release 26.6.12

## [26.6.11] - 2026-06-13

### ⚙️ Miscellaneous Tasks

- Release 26.6.11

## [26.6.10] - 2026-06-13

### ⚙️ Miscellaneous Tasks

- Release 26.6.10

## [26.6.9] - 2026-06-13

### ⚙️ Miscellaneous Tasks

- Release 26.6.9

## [26.6.8] - 2026-06-13

### 📚 Documentation

- Update pull request template instructions

### ⚙️ Miscellaneous Tasks

- Release 26.6.8

## [26.6.7] - 2026-06-13

### 🚀 Features

- Add get_git_root helper function
- Add git repository awareness to skill commands
- Support deep linking for github subdirectories
- Support adding skills from subdirectories

### 🐛 Bug Fixes

- Resolve rule management relative to git root
- Update add_module method signature in tests

### 🚜 Refactor

- Improve module path resolution and deployment

### 🧪 Testing

- Update add_module call in module service tests

### ⚙️ Miscellaneous Tasks

- Release 26.6.7

## [26.6.6] - 2026-06-13

### 🚀 Features

- Add submodule command to cli
- Add git sparse checkout support and utils
- Register submodule command in cli
- Refactor skill update command

### 🐛 Bug Fixes

- Support file protocol for remote repository URLs
- Remove cone mode from sparse checkout init
- Force submodule addition during initialization
- Add --skip-checks to sparse-checkout commands

### 🚜 Refactor

- Implement sparse checkout for module management
- Remove develop command and update rule flow
- Update rules and skills independently
- Improve path cleanup robustness

### 🧪 Testing

- Add unit tests for module service
- Initialize git repository in rule tests
- Initialize git repository in skills tests
- Add debug prints to rule test failure
- Refactor module service tests to avoid mocks
- Improve local skill path resolution and debugging
- Fix module service test mocking strategy

### ⚙️ Miscellaneous Tasks

- Release 26.6.6

## [26.6.5] - 2026-06-13

### 🚀 Features

- Add comprehensive Python development standards
- Add comprehensive Python development standards

### ⚙️ Miscellaneous Tasks

- [**breaking**] Update documentation and standards
- Release 26.6.5

## [26.6.4] - 2026-06-13

### 🚀 Features

- Add rules update command
- Add skills update command and file tree sync

### ⚙️ Miscellaneous Tasks

- Release 26.6.3
- Update dependencies and python version
- Remove all git submodules
- Release 26.6.4

### Build

- Add pdm.lock file

## [26.6.1] - 2026-06-13

### 🚀 Features

- Add cross-platform symlink creator script
- Add asynchronous rule generation script
- Add roo.py module manager script
- *(roo)* Automatically ignore module paths
- *(symlink)* Use file URI for local sources
- Support full repository git submodules
- *(submodule)* Resolve paths from git root
- *(cli)* Implement core rune commands and workspace
- *(submodule)* Add faststream skill
- *(workspace)* Automate .gitignore updates for agents
- *(workspace)* Dynamically update .gitignore for agents
- Add frappe-ui documentation and submodule
- *(architecture)* Add data-architecture skill guide
- *(skills)* Add Trigger.dev operational skill
- *(rune-cli)* Add skill validation service
- *(cli)* Add command to validate skill metadata
- *(cli)* Add skill command group
- *(crawlee)* Add skill docs and submodule
- *(arch)* Add integration design guidelines
- Refactor and expand CLI command modules
- Introduce configuration constants and exceptions
- Implement git-based configuration management
- Add Pydantic schemas for modules, rules, and skills
- Add questionary and update project configuration

### 🐛 Bug Fixes

- *(node)* Extend typescript configuration
- *(elevate)* Preserve working directory on restart
- Use git root instead of cwd for path resolution
- Normalize absolute paths relative to git root
- Use absolute paths instead of resolve
- *(submodules)* Update PlasmoHQ submodule URL
- *(rune-cli)* Copy symlinks when deploying modules

### 🚜 Refactor

- *(roo)* Update gitignore header text
- *(rules)* [**breaking**] Restructure microservices rules
- *(deps)* [**breaking**] Rename trigger.dev to trigger
- Rewrite module and service management logic
- Simplify CLI command registration in main entry point
- Migrate and clean up test suite

### 📚 Documentation

- *(rules)* Add Node.js architecture best practices
- *(rules)* Add Payload CMS implementation guidelines
- *(rules)* Add typescript best practice guides
- *(terraform)* Add coding standards and rules
- Migrate references from Terraform to OpenTofu
- *(rules)* Define OpenTofu usage policy
- Remove all markdown rule files
- Add microservice and nodejs architect rules
- *(rules)* [**breaking**] Add architecture guidelines for data-intensive systems
- *(terraform)* Add OpenTofu standards and rules
- *(ts)* Formalize typescript best practices
- Add Python architectural and robust rules
- *(rules)* Allow terraform for coder templates
- Add architecture and performance guidelines
- *(terraform)* Add OpenTofu and Terraform rules
- Remove Susan J. Fowler microservice rules
- [**breaking**] Add domain rules for react, data, and infra
- *(skills)* Add agent context note to Automatiq
- *(automatiq)* Add documentation for Automatiq skill
- *(skills)* Capitalize Automatiq skill name
- *(camoufox)* Add documentation and submodule
- *(cloakbrowser)* Add system context map documentation
- *(plasmo)* Add comprehensive skill guide and submodules
- *(hatchet)* Add operational guide and submodule
- *(skills)* Add metadata header to trigger.dev skill
- *(hatchet)* Add frontmatter to SKILL.md
- *(trigger)* Add period to description in SKILL.md
- *(hatchet)* Remove empty line from SKILL.md

### 🧪 Testing

- *(cli)* Verify .gitignore update on config
- *(cli)* Add recursive submodule support to `submodule add`
- *(cli)* Add unit tests for validate_skill service

### ⚙️ Miscellaneous Tasks

- Delete create_rules.py and roo.py
- Add release workflow and pull request template
- Move bumpver configuration to root
- Update release workflow permissions
- Release 26.6.1

### Build

- Remove create_symbolic_link.py script
- Configure project metadata and versioning

<!-- generated by git-cliff -->
