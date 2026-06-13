class RuneError(Exception):
    """Base class for Rune exceptions."""
    pass

class GitError(RuneError):
    """Raised when a git operation fails."""
    pass

class ConfigError(RuneError):
    """Raised when a configuration operation fails."""
    pass

class ModuleError(RuneError):
    """Raised when a module operation fails."""
    pass

class ValidationError(RuneError):
    """Raised when validation fails."""
    pass
