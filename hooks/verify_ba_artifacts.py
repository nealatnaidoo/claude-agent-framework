#!/usr/bin/env python3
"""
Governance Hook: Verify BA artifacts exist before coding agents start.

Triggered by SubagentStart hook for back and front.
Reads stdin for hook input JSON, checks the current project for required BA artifacts.

Exit codes:
  0 = artifacts found (or not in a project context)
  1 = missing artifacts, block agent start with error message
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
        # Stop at home directory
        if parent == Path.home():
            break
    return None


def find_claude_dir() -> Path | None:
    """Walk up from cwd looking for any .claude/ directory (not requiring manifest)."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        claude_dir = parent / ".claude"
        if claude_dir.is_dir():
            return claude_dir
        if parent == Path.home():
            break
    return None


def check_lost_lamb(claude_dir: Path) -> bool:
    """Check if a valid (non-expired) .lost_lamb exception exists."""
    lost_lamb = claude_dir / ".lost_lamb"
    if not lost_lamb.exists():
        return False
    try:
        data = json.loads(lost_lamb.read_text())
        created_str = data.get("created_at", "")
        created_at = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        elapsed = (now - created_at).total_seconds()
        return elapsed < 86400  # 24 hours
    except (json.JSONDecodeError, ValueError, KeyError, TypeError):
        return False


def check_ba_artifacts(project_root: Path) -> list[str]:
    """Check for required BA artifacts. Returns list of missing items."""
    artifacts_dir = project_root / ".claude" / "artifacts"
    missing = []

    if not artifacts_dir.exists():
        missing.append(".claude/artifacts/ directory")
        return missing

    # Check for spec (002_spec_*.md)
    specs = list(artifacts_dir.glob("002_spec_*.md"))
    if not specs:
        missing.append("002_spec_vN.md (specification)")

    # Check for tasklist (003_tasklist_*.md)
    tasklists = list(artifacts_dir.glob("003_tasklist_*.md"))
    if not tasklists:
        missing.append("003_tasklist_vN.md (tasklist)")

    return missing


def main():
    # Read hook input from stdin
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        hook_input = {}

    agent_name = hook_input.get("agent_name", "unknown")

    # Only enforce for coding agents
    coding_agents = ["back", "front"]
    if agent_name not in coding_agents:
        sys.exit(0)

    project_root = find_project_root()
    if project_root is None:
        # No manifest found — check for lost_lamb exception
        claude_dir = find_claude_dir()
        if claude_dir and check_lost_lamb(claude_dir):
            print(
                json.dumps(
                    {
                        "result": "warn",
                        "message": "Lost-lamb exception active. Coding allowed temporarily without BA artifacts.",
                    }
                )
            )
            sys.exit(0)
        # No manifest and no valid exception — block
        error_msg = (
            f"GOVERNANCE BLOCK: {agent_name} cannot start without a project manifest.\n"
            "No .claude/manifest.yaml found in any parent directory.\n"
            "\n"
            "Options:\n"
            "  1. Run init to scaffold governance\n"
            "  2. Use /lost-lamb for a 24hr ad-hoc exception\n"
            "  3. Use /broken-arrow to retrofit governance on an existing project"
        )
        print(json.dumps({"result": "block", "reason": error_msg}))
        sys.exit(1)

    missing = check_ba_artifacts(project_root)
    if missing:
        # Block the agent start
        error_msg = (
            f"GOVERNANCE BLOCK: {agent_name} cannot start without BA artifacts.\n"
            f"Missing: {', '.join(missing)}\n"
            f"Run the ba agent first to create specifications."
        )
        print(json.dumps({"result": "block", "reason": error_msg}))
        sys.exit(1)

    # All good
    sys.exit(0)


if __name__ == "__main__":
    main()
