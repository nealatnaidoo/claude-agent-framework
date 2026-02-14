#!/usr/bin/env python3
"""
Hook: TaskCompleted — fired when a teammate completes a task.

READ-ONLY advisory: reads manifest to identify newly unblocked tasks
and appends to evolution log. Does NOT write to manifest — the team
lead agent is responsible for manifest updates (governance compliance).

Exit codes:
  0 = advisory only (never blocks)
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def find_project_root() -> Path | None:
    """Walk up from cwd to find .claude/manifest.yaml."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".claude" / "manifest.yaml").exists():
            return parent
        if parent == Path.home():
            break
    return None


def check_manifest_unblocked(project_root: Path, task_id: str) -> list[str]:
    """Read manifest to identify tasks that would be unblocked. Does NOT write."""
    manifest_path = project_root / ".claude" / "manifest.yaml"
    if not manifest_path.exists():
        return []

    try:
        import yaml

        data = yaml.safe_load(manifest_path.read_text()) or {}
        outstanding = data.get("outstanding", {})
        if not isinstance(outstanding, dict):
            return []

        tasks = outstanding.get("tasks", [])
        if not isinstance(tasks, list):
            return []

        # Compute completed set (including the just-completed task)
        completed_ids = set()
        for task in tasks:
            if not isinstance(task, dict):
                continue
            if task.get("status") == "completed":
                completed_ids.add(task.get("id"))
        completed_ids.add(task_id)

        # Check for newly unblocked tasks
        unblocked = []
        for task in tasks:
            if not isinstance(task, dict):
                continue
            if task.get("status") != "pending":
                continue
            blocked_by = task.get("blocked_by", [])
            if blocked_by and all(bid in completed_ids for bid in blocked_by):
                unblocked.append(task.get("id", "?"))

        return unblocked
    except Exception:
        return []


def append_evolution_log(project_root: Path, task_id: str, teammate_name: str) -> None:
    """Append a completion entry to the evolution log."""
    evolution_path = project_root / ".claude" / "evolution" / "evolution.md"
    if not evolution_path.parent.exists():
        return

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"- [{now}] Task {task_id} completed by {teammate_name}\n"

    try:
        with open(evolution_path, "a") as f:
            f.write(entry)
    except OSError:
        pass


def main():
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        hook_input = {}

    task_id = hook_input.get("task_id", "")
    teammate_name = hook_input.get("teammate_name", "unknown")

    if not task_id:
        sys.exit(0)

    project_root = find_project_root()
    if project_root is None:
        sys.exit(0)

    unblocked = check_manifest_unblocked(project_root, task_id)
    append_evolution_log(project_root, task_id, teammate_name)

    parts = [f"Task {task_id} completed by {teammate_name}. Update manifest status to 'completed'."]
    if unblocked:
        parts.append(f"Newly unblocked: {', '.join(unblocked)}. Assign to idle teammates.")

    print(json.dumps({"result": "info", "message": " ".join(parts)}))
    sys.exit(0)


if __name__ == "__main__":
    main()
