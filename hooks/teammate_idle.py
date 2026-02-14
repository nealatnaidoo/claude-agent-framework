#!/usr/bin/env python3
"""
Hook: TeammateIdle — fired when a teammate completes work and is idle.

Reads the project manifest to find pending tasks matching the idle
teammate's domain and suggests the next task.

Exit codes:
  0 = advisory only (never blocks)
"""

import json
import sys
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


def read_manifest_tasks(project_root: Path) -> list[dict]:
    """Read tasks from manifest YAML."""
    manifest_path = project_root / ".claude" / "manifest.yaml"
    if not manifest_path.exists():
        return []
    try:
        import yaml

        data = yaml.safe_load(manifest_path.read_text()) or {}
        outstanding = data.get("outstanding", {})
        if isinstance(outstanding, dict):
            tasks = outstanding.get("tasks", [])
            return tasks if isinstance(tasks, list) else []
    except Exception:
        pass
    return []


def get_domain_for_teammate(teammate_name: str) -> str | None:
    """Map teammate name to task domain."""
    name_lower = teammate_name.lower()
    if any(k in name_lower for k in ("back", "backend", "python", "api")):
        return "backend"
    if any(k in name_lower for k in ("front", "frontend", "react", "ui")):
        return "frontend"
    return None


def find_next_task(tasks: list[dict], domain: str | None) -> dict | None:
    """Find the first unblocked pending task, optionally filtered by domain."""
    completed_ids = {
        t.get("id") for t in tasks if t.get("status") == "completed"
    }

    for task in tasks:
        if not isinstance(task, dict):
            continue
        if task.get("status") != "pending":
            continue

        # Check if blocked
        blocked_by = task.get("blocked_by", [])
        if blocked_by and not all(bid in completed_ids for bid in blocked_by):
            continue

        return task

    return None


def main():
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        hook_input = {}

    teammate_name = hook_input.get("teammate_name", "unknown")
    project_root = find_project_root()

    if project_root is None:
        sys.exit(0)

    tasks = read_manifest_tasks(project_root)
    if not tasks:
        sys.exit(0)

    domain = get_domain_for_teammate(teammate_name)
    next_task = find_next_task(tasks, domain)

    if next_task:
        task_id = next_task.get("id", "?")
        title = next_task.get("title", "Untitled")
        message = f"Teammate '{teammate_name}' is idle. Next task: {task_id} - {title}"
        print(json.dumps({"result": "info", "message": message}))
    else:
        print(json.dumps({
            "result": "info",
            "message": f"Teammate '{teammate_name}' is idle. No pending tasks remain.",
        }))

    sys.exit(0)


if __name__ == "__main__":
    main()
