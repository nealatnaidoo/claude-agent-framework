#!/usr/bin/env python3
"""
Governance Hook: Verify DevOps approval exists before BA agent starts.

Triggered by SubagentStart hook for business-analyst.
Checks that the solution envelope contains a devops_approval section.

Exit codes:
  0 = approval found (or no envelope exists yet, which is also OK - BA handles that)
  1 = envelope exists WITHOUT DevOps approval, block BA start
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
        if parent == Path.home():
            break
    return None


def check_devops_approval(project_root: Path) -> tuple[bool, str]:
    """
    Check for DevOps approval in solution envelope.

    Returns (ok, message):
      - (True, "") if approval found or no envelope exists
      - (False, reason) if envelope exists but lacks approval
    """
    artifacts_dir = project_root / ".claude" / "artifacts"
    if not artifacts_dir.exists():
        return True, ""  # No artifacts yet - BA will handle this

    envelopes = sorted(artifacts_dir.glob("001_solution_envelope_*.md"))
    if not envelopes:
        return True, ""  # No envelope yet - BA startup protocol handles this

    # Check the latest envelope for devops_approval
    latest = envelopes[-1]
    content = latest.read_text()

    if "devops_approval:" in content:
        return True, ""

    # Also check for common variations
    if "approved_by: \"devops-governor\"" in content:
        return True, ""
    if "approved_by: 'devops-governor'" in content:
        return True, ""

    return False, (
        f"GOVERNANCE BLOCK: Solution envelope exists ({latest.name}) "
        f"but lacks DevOps approval.\n"
        f"Solution Designer must consult devops-governor and obtain "
        f"approval stamp before BA can proceed."
    )


def main():
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        hook_input = {}

    agent_name = hook_input.get("agent_name", "unknown")
    if agent_name != "business-analyst":
        sys.exit(0)

    project_root = find_project_root()
    if project_root is None:
        sys.exit(0)

    ok, message = check_devops_approval(project_root)
    if ok:
        sys.exit(0)

    print(json.dumps({"result": "block", "reason": message}))
    sys.exit(1)


if __name__ == "__main__":
    main()
