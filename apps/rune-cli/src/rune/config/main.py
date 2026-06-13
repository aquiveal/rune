from pathlib import Path
import os

RUNE_DIR = ".rune"
RUNE_CONFIG = "config"
RUNE_MODULES_FILE = ".runemodules"
RUNE_MODULES_DIR = "modules"
RUNE_TMP_DIR = "tmp"
RUNE_INDEX = "index"

DEFAULT_AGENTS = [".roo", ".claude", ".cursor", ".cline"]

def get_global_rune_dir() -> Path:
    return Path.home() / RUNE_DIR
