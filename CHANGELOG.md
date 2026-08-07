## Infrastructure

* **Dependency Upgrades for Core Libraries**
  Upgraded project dependencies including `coverage`, `googleapis-common-protos`, `grpcio`, `langfuse`, `opentelemetry`, `pydantic-settings`, and `pyrefly`.
  Commits: [3476d01](https://github.com/aquiveal/rune/commit/3476d014), [e7f69b4](https://github.com/aquiveal/rune/commit/e7f69b4e)

* **Logging Dependency Addition**
  Added `python-logging` as a git dependency to the project configuration.
  Commit: [1a5bfef](https://github.com/aquiveal/rune/commit/1a5bfef9)

* **Settings Class Refactoring**
  Refactored the core `Settings` class to inherit from `LoggingSettings` for improved configuration management.
  Commit: [1a5bfef](https://github.com/aquiveal/rune/commit/1a5bfef9)
