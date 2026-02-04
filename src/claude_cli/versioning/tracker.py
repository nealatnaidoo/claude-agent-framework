"""Core version tracking functionality."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from claude_cli.common.config import get_framework_paths

TRACKED_PATHS = {
    "agents": "agents",
    "prompts/system": "prompts/system",
    "prompts/playbooks": "prompts/playbooks",
    "schemas": "schemas",
    "lenses": "lenses",
    "knowledge": "knowledge",
    "docs": "docs",
}

TRACKED_EXTENSIONS = {".md", ".yaml", ".yml", ".json", ".py"}


def get_history_file() -> Path:
    """Get path to history file."""
    paths = get_framework_paths()
    return Path(paths["versions"]) / "history.json"


def compute_checksum(file_path: Path) -> str:
    """Compute SHA-256 checksum of file content."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()[:16]


def load_history() -> dict:
    """Load version history from JSON file."""
    history_file = get_history_file()
    if history_file.exists():
        with open(history_file) as f:
            return json.load(f)
    return {"schema_version": "1.0", "records": [], "snapshots": []}


def save_history(history: dict) -> None:
    """Save version history to JSON file."""
    history_file = get_history_file()
    history_file.parent.mkdir(parents=True, exist_ok=True)
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2, default=str)


def get_current_components() -> dict:
    """Scan repo and return current state of all tracked components."""
    paths = get_framework_paths()
    repo_root = Path(paths["root"])
    components = {}

    for component_type, rel_path in TRACKED_PATHS.items():
        dir_path = repo_root / rel_path
        if not dir_path.exists():
            continue

        for file_path in dir_path.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.suffix not in TRACKED_EXTENSIONS:
                continue
            if file_path.name.startswith("."):
                continue

            relative = file_path.relative_to(repo_root)
            component_name = file_path.stem

            components[str(relative)] = {
                "component_type": component_type,
                "component_name": component_name,
                "file_path": str(relative),
                "checksum": compute_checksum(file_path),
            }

    return components


def get_latest_record(history: dict, file_path: str) -> Optional[dict]:
    """Get the most recent record for a file path (where valid_to is null)."""
    for record in reversed(history["records"]):
        if record["file_path"] == file_path and record["valid_to"] is None:
            return record
    return None


def scan_changes(history: dict) -> list:
    """Compare current state against history, return list of changes."""
    current = get_current_components()
    changes = []
    now = datetime.now(timezone.utc).isoformat()

    current_paths = set(current.keys())
    historical_paths = {r["file_path"] for r in history["records"] if r["valid_to"] is None}

    for file_path, component in current.items():
        latest = get_latest_record(history, file_path)

        if latest is None:
            changes.append({
                **component,
                "version": "1.0.0",
                "valid_from": now,
                "valid_to": None,
                "recorded_at": now,
                "change_type": "initial",
                "change_summary": "Initial version",
            })
        elif latest["checksum"] != component["checksum"]:
            changes.append({
                "action": "close",
                "file_path": file_path,
                "valid_to": now,
            })

            old_version = latest.get("version", "1.0.0")
            parts = old_version.split(".")
            parts[-1] = str(int(parts[-1]) + 1)
            new_version = ".".join(parts)

            changes.append({
                **component,
                "version": new_version,
                "valid_from": now,
                "valid_to": None,
                "recorded_at": now,
                "change_type": "modified",
                "change_summary": f"Updated (checksum changed from {latest['checksum']})",
            })

    for file_path in historical_paths - current_paths:
        latest = get_latest_record(history, file_path)
        if latest:
            changes.append({
                "action": "close",
                "file_path": file_path,
                "valid_to": now,
            })
            changes.append({
                **{k: latest[k] for k in ["component_type", "component_name", "file_path"]},
                "checksum": None,
                "version": latest.get("version", "1.0.0") + "-deleted",
                "valid_from": now,
                "valid_to": now,
                "recorded_at": now,
                "change_type": "deleted",
                "change_summary": "File removed",
            })

    return changes


def apply_changes(history: dict, changes: list) -> int:
    """Apply changes to history, return count of changes applied."""
    applied = 0

    for change in changes:
        if change.get("action") == "close":
            for record in history["records"]:
                if record["file_path"] == change["file_path"] and record["valid_to"] is None:
                    record["valid_to"] = change["valid_to"]
                    break
        else:
            history["records"].append({k: v for k, v in change.items() if k != "action"})
            applied += 1

    return applied


def get_state_at(history: dict, target_date: datetime) -> list:
    """Get system state at a specific point in time."""
    target_iso = target_date.isoformat()
    state = []

    for record in history["records"]:
        valid_from = record["valid_from"]
        valid_to = record["valid_to"]

        if valid_from <= target_iso:
            if valid_to is None or target_iso < valid_to:
                state.append(record)

    return sorted(state, key=lambda r: (r["component_type"], r["component_name"]))
