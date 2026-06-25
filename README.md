# Rune

Rune is a Git-like command-line tool designed to manage LLM coding agent context, rules, and skills. It acts as a shadow version control system, allowing you to seamlessly integrate, update, and manage guidelines and executable skills for your AI agents across different projects without polluting your primary git history.

## Features

- **Agent Context Management**: Easily manage rules and skills for various LLM agents (e.g., Roo, Cursor, Windsurf).
- **Git-like Workflow**: Familiar commands like `init`, `status`, `update`, `fetch`, `pull`, `diff`, `remote`, `skills`, `rules`, and `modules`.
- **Global and Local Scopes**: Install rules and skills globally for all projects (`~/.roo/skills`, `.cursor/rules`) or locally for a specific repository.
- **Rune Modules (`.runemodules`)**: Manage external dependencies as internal tracked clones. This ensures easy upstream syncing, deterministic versions, and isolation from standard git submodules.
- **Skill Scaffolding**: Quickly scaffold new skills with a standard directory structure and automatically validate them against specification constraints.
- **Rule Merging**: Automatically merge installed rules into an `AGENTS.md` file for easy consumption by generic LLMs.
- **Dependency Sandboxing**: Skills are sandboxed into their own directories.

## Installation

Rune uses PDM (Python Dependency Manager) and standard Python deployment tools like `uv` and `pipx`.

### Prerequisites

1. Python 3.11 or higher.

### Option 1: Global Installation via `uv` or `pipx` (Recommended)

To install Rune globally on your system so you can use the `rune` command anywhere:

```bash
# Using uv (extremely fast)
uv tool install "git+https://github.com/aquiveal/rune.git#subdirectory=apps/rune-cli"

# Using pipx
pipx install "git+https://github.com/aquiveal/rune.git#subdirectory=apps/rune-cli"
```

You can also install it from a local clone:

```bash
git clone https://github.com/aquiveal/rune.git
cd rune/apps/rune-cli

uv tool install .
# or
pipx install .
```

*Ensure your Python global scripts directory is in your `PATH`.*

### Option 2: Editable Installation (Development)

If you want to contribute to Rune or run it locally:

```bash
git clone https://github.com/aquiveal/rune.git
cd rune/apps/rune-cli
pdm install

pdm run rune --help
```

## Core Concepts

- **Rules**: Markdown files containing guidelines for LLMs. Rune organizes rules into specific directories and merges them into an `AGENTS.md` file to inject context.
- **Skills**: Advanced executable capabilities (e.g., Python scripts, bash scripts) mapped using an AST parser (like Aider) or executed directly by agent tools. Skills must include a `SKILL.md` entrypoint.
- **Modules**: A generic term for any context package (Rules or Skills). Handled via `.runemodules`.
- **Remotes**: URL aliases pointing to central repositories holding community or personal rules and skills.
- **AGENTS.md**: A compiled manifest file injected into LLM context prompts detailing the project's activated rules.

## Usage

### Initialization

Initialize a new Rune shadow repository in your current directory. This creates a `.rune` folder to store configuration and state.

```bash
rune init
```

### Managing Rules (`rune rules`)

Rules dictate coding standards, architectural guidelines, and best practices.

**Install Rules**
```bash
# Install a rule locally from a git repo (using a remote alias or full URL)
rune rules add <source_url_or_alias>

# Install a specific rule by name
rune rules add aquiveal/rune --rule language-python

# Target a specific AI agent (e.g. roo, cursor)
rune rules add aquiveal/rune --agent cursor

# Install globally to your home directory (~/.cursor/rules, ~/.roo/skills)
rune rules add aquiveal/rune --global

# Copy files directly instead of tracking them via .runemodules
rune rules add aquiveal/rune --copy
```

**View & Update Rules**
```bash
# List all installed rules (local)
rune rules list

# Update all tracked rules to their latest upstream commits and merge into AGENTS.md
rune rules update

# Remove a specific installed rule
rune rules remove <rule_name>
```

**Authoring Rules**
```bash
# Scaffold a new rule directory with standard boilerplate files
rune rules init <rule_name>
```

### Managing Skills (`rune skills`)

Skills provide executable logic and advanced tool instructions for agents.

**Install Skills**
```bash
# Install a skill from a repo
rune skills add <source_url_or_alias>
```

**View, Update & Remove Skills**
```bash
# List all installed skills
rune skills list

# Update all tracked skills to their latest upstream commits
rune skills update

# Remove a specific installed skill
rune skills remove <skill_name>
```

**Authoring Skills**
```bash
# Scaffold a new skill directory with a standard SKILL.md template
rune skills init <skill_name>

# Validate an existing skill against the Agents specification
rune skills validate <path_to_skill>
```

### Contextual Modules (`rune modules`)

A generic command for managing modules contextually.

```bash
# Contextually adds a module depending on the current directory
rune modules add <source_url_or_alias>

# Add and scaffold a skill directly from the project root 
# (automatically infers the correct agent directory, scaffolds the skill, and links the module)
rune modules add <source_url_or_alias> <skill_name>
```

### Base CLI Commands

**Status**
```bash
# View the overall status of your local Rune repository, including installed modules
rune status
```

**Git-like Synchronization**
```bash
# Update everything across your environment (Skills and Rules)
rune update
rune update --global

# Fetch updates for runemodules without applying them
rune fetch

# Pull and merge updates for runemodules
rune pull

# Show changes between local agent rules and upstream
rune diff
```

**Config & Remotes**
```bash
# Get or set options in `.rune/config`
rune config <key> [value]

# Manage remote repository aliases (simplifies `add` commands)
rune remote add <alias> <url>
```

## License

This project is licensed under the MIT License.
