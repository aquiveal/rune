# Changelog

All notable changes to this project will be documented in this file.

## [26.6.40] - 2026-06-23

### 🚀 Features

- Add architectural and domain standards

### 📚 Documentation

- Add elite architecture and coding standards
- Update python-logging skill documentation

### ⚙️ Miscellaneous Tasks

- Update python-logging module url

## [26.6.39] - 2026-06-21

### 🚀 Features

- Allow dynamic max token configuration
- Add support for repomap max tokens config

### ⚙️ Miscellaneous Tasks

- Release 26.6.39

## [26.6.38] - 2026-06-21

### 🐛 Bug Fixes

- Ignore dangling symlinks during directory copy

### 🧪 Testing

- Update module service tests

### ⚙️ Miscellaneous Tasks

- Release 26.6.38

## [26.6.37] - 2026-06-20

### 🚀 Features

- Move AST map content outside of file tree

### ⚙️ Miscellaneous Tasks

- Remove debug print statement
- Release 26.6.37

## [26.6.36] - 2026-06-20

### 🐛 Bug Fixes

- Initialize sparse checkout before adding paths
- Use source_path for submodule map generation
- Prevent sparse checkout errors for root paths
- Conditionally initialize sparse checkout

### ⚙️ Miscellaneous Tasks

- Add debug print and use absolute paths
- Release 26.6.36

## [26.6.35] - 2026-06-20

### 🚀 Features

- Add python-logging skill documentation
- Enable sparse checkout for git modules

### 🐛 Bug Fixes

- Handle relative paths for module type inference
- Update file indexing path and ignore rules

### ⚙️ Miscellaneous Tasks

- Fix syntax in runemodules configuration
- Remove skills directory from gitignore
- Release 26.6.35

## [26.6.34] - 2026-06-20

### 🚀 Features

- Add aider-chat and dependencies

### 🐛 Bug Fixes

- Clone missing repository modules
- Handle read-only files during directory removal
- Use lambda to prevent regex substitution errors

### 🚜 Refactor

- Update repomap model and method arguments

### ⚙️ Miscellaneous Tasks

- Release 26.6.34

### Build

- Restrict python version to <3.13

## [26.6.33] - 2026-06-20

### ⚙️ Miscellaneous Tasks

- Downgrade pydantic version
- Release 26.6.33

## [26.6.32] - 2026-06-20

### 🚀 Features

- Resolve submodule urls and subpaths

### 🐛 Bug Fixes

- Update both skill and module submodules
- Handle root directory paths in module urls

### ⚙️ Miscellaneous Tasks

- Release 26.6.32

## [26.6.31] - 2026-06-20

### ⚙️ Miscellaneous Tasks

- Migrate python-logging module to runemodules
- Release 26.6.31

## [26.6.30] - 2026-06-20

### 🚀 Features

- Add get_repomap_model helper
- Add modules type inference for module schema
- Add submodule map generation service
- Improve module deployment and configuration
- Include .repomap.txt content in directory tree

### 🚜 Refactor

- Remove submodule update from skill command
- Replace direct submodule addition with module service

### ⚙️ Miscellaneous Tasks

- Add aider-chat dependency
- Release 26.6.30

## [26.6.29] - 2026-06-15

### 🚜 Refactor

- Update rule heading levels in generated docs

### 🧪 Testing

- Update rule service assertions

### ⚙️ Miscellaneous Tasks

- Release 26.6.29

## [26.6.28] - 2026-06-15

### 🐛 Bug Fixes

- Ignore empty markdown rule files

### ⚙️ Miscellaneous Tasks

- Release 26.6.28

## [26.6.27] - 2026-06-15

### 🚀 Features

- Support standalone markdown files in rules

### ⚙️ Miscellaneous Tasks

- Release 26.6.27

## [26.6.26] - 2026-06-15

### 🚀 Features

- Update skill discovery paths and search logic

### 🧪 Testing

- Add test for skill discovery depth

### ⚙️ Miscellaneous Tasks

- Release 26.6.26

## [26.6.25] - 2026-06-15

### ⚙️ Miscellaneous Tasks

- Remove readme field from pyproject.toml
- Release 26.6.25

## [26.6.24] - 2026-06-15

### 🚀 Features

- Add get_short_sha helper to git repository
- Display git submodule SHAs in file tree

### ⚙️ Miscellaneous Tasks

- Ignore plans directory
- Release 26.6.24

## [26.6.23] - 2026-06-14

### 📚 Documentation

- Update root documentation

### ⚙️ Miscellaneous Tasks

- Release 26.6.23

### Build

- Add python-logging submodule

## [26.6.22] - 2026-06-13

### 🚀 Features

- Sanitize skill names during initialization

### 🐛 Bug Fixes

- Sanitize skill names before directory creation

### ⚙️ Miscellaneous Tasks

- Release 26.6.22

## [26.6.21] - 2026-06-13

### 🐛 Bug Fixes

- Retry submodule add on index error

### ⚙️ Miscellaneous Tasks

- Release 26.6.21

## [26.6.20] - 2026-06-13

### 🐛 Bug Fixes

- Handle GitHub tree URLs in module schema

### 🚜 Refactor

- Remove redundant space-separated URL logic

### ⚙️ Miscellaneous Tasks

- Release 26.6.20

## [26.6.19] - 2026-06-13

### 🐛 Bug Fixes

- Handle submodule addition and update errors

### ⚙️ Miscellaneous Tasks

- Release 26.6.19

## [26.6.18] - 2026-06-13

### 🚜 Refactor

- Remove agent directory exclusion from ignores

### ⚙️ Miscellaneous Tasks

- Refactor and update agent documentation structure
- Remove agents directory from gitignore
- Release 26.6.18

## [26.6.17] - 2026-06-13

### 🚀 Features

- Add .agents to default agents list
- Use default agents for skill target selection
- Auto-update gitignore on command execution

### 🐛 Bug Fixes

- Remove quotes from module config sections
- Refine directory handling and gitignore rules

### 🚜 Refactor

- Use constant for default agents list
- Use default agents list for rule discovery

### ⚙️ Miscellaneous Tasks

- Import default agents for rule command
- Release 26.6.17

## [26.6.16] - 2026-06-13

### 🚀 Features

- Add agent selection persistence to config
- Add selected agents to configuration

### 🧪 Testing

- Update rule content verification
- Add test cases for module schema properties
- Add unit tests for rule service merge logic

### ⚙️ Miscellaneous Tasks

- Release 26.6.16

## [26.6.15] - 2026-06-13

### 🚜 Refactor

- Update rules block injection in AGENTS.md
- Update regex to only match # Rules block
- Improve rule content formatting

### ⚙️ Miscellaneous Tasks

- Release 26.6.15

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
