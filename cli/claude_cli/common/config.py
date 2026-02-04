"""Configuration and path management for Claude CLI."""

from pathlib import Path
from typing import Any


def get_framework_root() -> Path:
    """Get the framework root directory."""
    # Try ~/.claude symlink first
    claude_home = Path.home() / ".claude"
    if claude_home.is_symlink() or claude_home.is_dir():
        return claude_home.resolve()

    # Fallback to relative path from this file
    return Path(__file__).parent.parent.parent.parent.resolve()


def get_framework_paths() -> dict[str, str]:
    """Get all framework paths."""
    root = get_framework_root()
    return {
        "root": str(root),
        "agents": str(root / "agents"),
        "knowledge": str(root / "knowledge"),
        "prompts": str(root / "prompts"),
        "schemas": str(root / "schemas"),
        "cli_data": str(root / "cli" / "data"),
        "patterns": str(root / "patterns"),
    }


def get_db_path(db_name: str = "lessons.duckdb") -> Path:
    """Get path to a CLI database file."""
    root = get_framework_root()
    data_dir = root / "cli" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / db_name


def get_knowledge_path() -> Path:
    """Get path to knowledge directory."""
    return get_framework_root() / "knowledge"


def get_devlessons_path() -> Path:
    """Get path to devlessons.md."""
    return get_knowledge_path() / "devlessons.md"
