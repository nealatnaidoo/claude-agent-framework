"""Batch ledger management for tracking parallel headless jobs.

Provides YAML-based ledger CRUD with atomic writes and resume support.
Each batch gets a directory under {project}/.claude/batch/{batch_id}/
containing a ledger.yaml and results/ subdirectory.
"""

from __future__ import annotations

import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml


SCHEMA_VERSION = "1.0"


def generate_batch_id() -> str:
    """Generate a unique batch ID based on current timestamp."""
    return "batch-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def create_ledger(
    batch_id: str,
    items: list[str],
    prompt_template: str,
    config: dict,
    batch_dir: Path,
) -> Path:
    """Create a new batch ledger YAML file.

    Args:
        batch_id: Unique batch identifier.
        items: List of item paths/names to process.
        prompt_template: Prompt template with $item placeholder.
        config: Batch configuration (parallel, max_turns, allowed_tools).
        batch_dir: Directory for this batch (created if needed).

    Returns:
        Path to the created ledger.yaml file.
    """
    batch_dir.mkdir(parents=True, exist_ok=True)
    (batch_dir / "results").mkdir(exist_ok=True)

    now = datetime.now(timezone.utc).isoformat()
    ledger = {
        "schema_version": SCHEMA_VERSION,
        "batch_id": batch_id,
        "created_at": now,
        "updated_at": now,
        "config": {
            "prompt_template": prompt_template,
            "pattern": config.get("pattern", ""),
            "parallel": config.get("parallel", 5),
            "max_turns": config.get("max_turns", 20),
            "allowed_tools": config.get("allowed_tools", []),
        },
        "summary": {
            "total": len(items),
            "pending": len(items),
            "active": 0,
            "done": 0,
            "failed": 0,
        },
        "items": [
            {
                "name": item,
                "status": "pending",
                "started_at": None,
                "completed_at": None,
                "pid": None,
                "result_file": f"results/{_sanitize_name(item)}.json",
                "summary": None,
                "exit_code": None,
            }
            for item in items
        ],
    }

    ledger_path = batch_dir / "ledger.yaml"
    _atomic_write(ledger_path, ledger)
    return ledger_path


def load_ledger(ledger_path: Path) -> dict:
    """Load ledger from YAML file.

    Args:
        ledger_path: Path to ledger.yaml.

    Returns:
        Parsed ledger dictionary.

    Raises:
        FileNotFoundError: If ledger file does not exist.
    """
    if not ledger_path.exists():
        raise FileNotFoundError(f"Ledger not found: {ledger_path}")
    return yaml.safe_load(ledger_path.read_text()) or {}


def update_item_status(
    ledger_path: Path,
    item_name: str,
    status: str,
    result_summary: str | None = None,
    pid: int | None = None,
    exit_code: int | None = None,
) -> None:
    """Update a single item's status in the ledger.

    Args:
        ledger_path: Path to ledger.yaml.
        item_name: Name of the item to update.
        status: New status (pending, active, done, failed).
        result_summary: One-line summary of the result.
        pid: OS process ID (set when status becomes active).
        exit_code: Process exit code (set when status becomes done/failed).
    """
    ledger = load_ledger(ledger_path)
    now = datetime.now(timezone.utc).isoformat()

    for item in ledger.get("items", []):
        if item["name"] == item_name:
            item["status"] = status
            if status == "active":
                item["started_at"] = now
                if pid is not None:
                    item["pid"] = pid
            elif status in ("done", "failed"):
                item["completed_at"] = now
                if exit_code is not None:
                    item["exit_code"] = exit_code
            if result_summary is not None:
                item["summary"] = result_summary
            break

    # Recompute summary counts
    ledger["summary"] = _compute_summary(ledger["items"])
    ledger["updated_at"] = now
    _atomic_write(ledger_path, ledger)


def get_resumable_items(ledger_path: Path) -> list[str]:
    """Return item names that are pending or failed (eligible for retry).

    Args:
        ledger_path: Path to ledger.yaml.

    Returns:
        List of item names with status pending or failed.
    """
    ledger = load_ledger(ledger_path)
    return [
        item["name"]
        for item in ledger.get("items", [])
        if item.get("status") in ("pending", "failed")
    ]


def get_active_items(ledger_path: Path) -> list[dict]:
    """Return items currently marked as active (for stale detection).

    Args:
        ledger_path: Path to ledger.yaml.

    Returns:
        List of item dicts with status active.
    """
    ledger = load_ledger(ledger_path)
    return [
        item for item in ledger.get("items", []) if item.get("status") == "active"
    ]


def get_ledger_summary(ledger_path: Path) -> dict:
    """Return status counts from the ledger.

    Args:
        ledger_path: Path to ledger.yaml.

    Returns:
        Dict with keys: total, pending, active, done, failed.
    """
    ledger = load_ledger(ledger_path)
    return ledger.get("summary", _compute_summary(ledger.get("items", [])))


def reset_stale_active(ledger_path: Path) -> list[str]:
    """Reset items stuck in 'active' with dead PIDs back to 'pending'.

    Checks if the PID is still running. If not, resets to pending.

    Returns:
        List of item names that were reset.
    """
    ledger = load_ledger(ledger_path)
    reset_items = []

    for item in ledger.get("items", []):
        if item.get("status") == "active" and item.get("pid"):
            if not _is_process_alive(item["pid"]):
                item["status"] = "pending"
                item["pid"] = None
                item["started_at"] = None
                reset_items.append(item["name"])

    if reset_items:
        ledger["summary"] = _compute_summary(ledger["items"])
        ledger["updated_at"] = datetime.now(timezone.utc).isoformat()
        _atomic_write(ledger_path, ledger)

    return reset_items


def _compute_summary(items: list[dict]) -> dict:
    """Compute status counts from item list."""
    counts = {"total": len(items), "pending": 0, "active": 0, "done": 0, "failed": 0}
    for item in items:
        status = item.get("status", "pending")
        if status in counts:
            counts[status] += 1
    return counts


def _sanitize_name(item: str) -> str:
    """Convert item path to safe filename component.

    Example: src/auth/service.py -> src_auth_service_py
    """
    return item.replace("/", "_").replace("\\", "_").replace(".", "_").rstrip("_")


def _atomic_write(path: Path, data: dict) -> None:
    """Write YAML atomically via temp file + rename."""
    fd, tmp_path = tempfile.mkstemp(
        dir=path.parent, suffix=".tmp", prefix=".ledger_"
    )
    try:
        with os.fdopen(fd, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        os.rename(tmp_path, path)
    except Exception:
        # Clean up temp file on failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _is_process_alive(pid: int) -> bool:
    """Check if a process with given PID is still running."""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False
