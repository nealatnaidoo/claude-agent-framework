#!/usr/bin/env python3
"""
Governance Hook: Verify BA artifacts exist before coding agents start.

Triggered by SubagentStart hook for backend-coding-agent and frontend-coding-agent.
Reads stdin for hook input JSON, checks the current project for required BA artifacts.

Exit codes:
  0 = artifacts found (or not in a project context)
  1 = missing artifacts, block agent start with error message
"""

import json
import sys
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
    coding_agents = ["backend-coding-agent", "frontend-coding-agent"]
    if agent_name not in coding_agents:
        sys.exit(0)

    project_root = find_project_root()
    if project_root is None:
        # Not in a project context - allow but warn
        print(
            json.dumps(
                {
                    "result": "warn",
                    "message": "No project manifest found. Coding agents require BA artifacts.",
                }
            )
        )
        sys.exit(0)

    missing = check_ba_artifacts(project_root)
    if missing:
        # Block the agent start
        error_msg = (
            f"GOVERNANCE BLOCK: {agent_name} cannot start without BA artifacts.\n"
            f"Missing: {', '.join(missing)}\n"
            f"Run the business-analyst agent first to create specifications."
        )
        print(json.dumps({"result": "block", "reason": error_msg}))
        sys.exit(1)

    # All good
    sys.exit(0)


if __name__ == "__main__":
    main()
