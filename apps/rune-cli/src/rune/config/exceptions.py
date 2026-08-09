__all__ = ["ConfigError", "GitError", "ModuleError", "RuneError", "ValidationError"]


class RuneError(Exception):
    """Base class for Rune exceptions."""


class GitError(RuneError):
    """Raised when a git operation fails."""


class ConfigError(RuneError):
    """Raised when a configuration operation fails."""


class ModuleError(RuneError):
    """Raised when a module operation fails."""


class ValidationError(RuneError):
    """Raised when validation fails."""
