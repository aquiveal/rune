# Rune

Rune is a Git-like command-line tool designed to manage LLM coding agent context, rules, and skills. It acts as a shadow version control system, allowing you to seamlessly integrate, update, and manage guidelines and executable skills for your AI agents across different projects.

## Features

- **Agent Context Management**: Easily manage rules and skills for various LLM agents (e.g., Roo, Cursor, Windsurf).
- **Git-like Workflow**: Familiar commands like `init`, `status`, `update`, `remote`, `skills`, and `rules`.
- **Global and Local Scopes**: Install rules and skills globally for all projects or locally for a specific repository.
- **Submodule Support**: Manage rules and skills as Git submodules, ensuring they stay up-to-date with upstream changes.
- **Skill Scaffolding**: Quickly scaffold new skills with a standard directory structure.
- **Rule Merging**: Automatically merge installed rules into an `AGENTS.md` file for easy consumption by LLMs.

## Installation

Rune is managed using PDM, a modern Python package and dependency manager.

### Prerequisites

1. Python 3.11 or higher.
2. PDM (Python Dependency Manager). Install it using pip:
   ```sh
   pip install pdm
   ```

### Installing the CLI

You can install Rune CLI globally in your system or use it within a virtual environment.

#### Option 1: Global Installation via pipx or uv (Recommended)

To install Rune globally on your system so you can use the `rune` command anywhere:

```sh
# Install globally using pipx from git
pipx install "git+https://github.com/aquiveal/rune.git#subdirectory=apps/rune-cli"

# Or using uv from git
uv tool install "git+https://github.com/aquiveal/rune.git#subdirectory=apps/rune-cli"
```

You can also install it from a local clone:

```sh
# Clone the repository
git clone https://github.com/aquiveal/rune.git
cd rune/apps/rune-cli

# Install globally using pipx
pipx install .

# Or using uv
uv tool install .
```

Make sure your Python global scripts directory is in your `PATH` (typically `~/.local/bin` on Linux/macOS/WSL or `%APPDATA%\Python\Scripts` on Windows).

#### Option 2: Editable Installation (Development)

If you want to contribute to Rune or run it locally:

```sh
git clone https://github.com/aquiveal/rune.git
cd rune/apps/rune-cli
pdm install
```

You can then run commands using:

```sh
pdm run rune --help
```

## Usage

### Initialization

Initialize a new Rune repository in your current directory:

```sh
rune init
```

This creates a `.rune` directory to store configuration and state.

### Managing Rules

Rules are markdown files that define coding standards, architectural guidelines, and best practices for your agents.

- **Add a rule**:
  ```sh
  rune rules add <source_url_or_alias>
  ```
  Example: `rune rules add aquiveal/rune --rule language-python`

- **List installed rules**:
  ```sh
  rune rules list
  ```

- **Update rules**:
  ```sh
  rune rules update
  ```
  This updates the rule submodules and merges them into `AGENTS.md`.

- **Remove a rule**:
  ```sh
  rune rules remove <rule_name>
  ```

- **Scaffold a new rule**:
  ```sh
  rune rules init <rule_name>
  ```

### Managing Skills

Skills are executable agent capabilities, often containing scripts, references, and a `SKILL.md` file.

- **Add a skill**:
  ```sh
  rune skills add <source_url_or_alias>
  ```

- **List installed skills**:
  ```sh
  rune skills list
  ```

- **Update skills**:
  ```sh
  rune skills update
  ```

- **Remove a skill**:
  ```sh
  rune skills remove <skill_name>
  ```

- **Scaffold a new skill**:
  ```sh
  rune skills init <skill_name>
  ```

- **Validate a skill**:
  ```sh
  rune skills validate <path_to_skill>
  ```

### Submodules

Manage submodules contextually within skills:

```sh
cd .agents/skills
rune submodule add <git_url> <target_skill_name>
```

### Configuration

Manage Rune configuration options:

```sh
rune config <key> [value]
```

### Remote Repositories

Add remote repository aliases for easier rule and skill installation:

```sh
rune remote add <alias> <url>
```

## Project Structure

- `apps/rune-cli/`: The source code for the Rune command-line interface.
- `rules/`: A collection of standard rules for various languages and frameworks.
- `specs/`: Specifications for Rune features and formats.

## License

This project is licensed under the MIT License.
