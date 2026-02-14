#!/usr/bin/env python3
"""
Governance Hook: Manage deployment gate file based on active agent.

Triggered by SubagentStart for ALL agents (matcher: ".*").
Creates .deploy_gate when ops starts, deletes it for all others.

This hook NEVER blocks agent starts (always exits 0).

Exit codes:
  0 = gate managed successfully
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def find_project_root() -> Path | None:
    """Walk up from cwd to find a .claude/manifest.yaml."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        manifest = parent / ".claude" / "manifest.yaml"
        if manifest.exists():
            return parent
        if parent == Path.home():
            break
    return None


def main():
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        hook_input = {}

    agent_name = hook_input.get("agent_name", "unknown")

    project_root = find_project_root()
    if project_root is None:
        sys.exit(0)

    gate_file = project_root / ".claude" / ".deploy_gate"

    if agent_name == "ops":
        gate_data = {
            "agent": "ops",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "session_id": hook_input.get("session_id", ""),
        }
        gate_file.parent.mkdir(parents=True, exist_ok=True)
        gate_file.write_text(json.dumps(gate_data))
    else:
        if gate_file.exists():
            gate_file.unlink()

    sys.exit(0)


if __name__ == "__main__":
    main()
