#!/usr/bin/env python3
"""
Governance Hook: Verify evidence artifacts exist before QA reviewer starts.

Triggered by SubagentStart hook for qa-reviewer.
Checks that coding agents produced evidence artifacts before QA begins.

Exit codes:
  0 = evidence found (or advisory warning only)
  1 = no evidence at all, block QA start
"""

import json
import sys
from pathlib import Path

REQUIRED_EVIDENCE = [
    "quality_gates_run.json",
    "test_report.json",
]


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


def check_evidence(project_root: Path) -> tuple[bool, list[str]]:
    """
    Check for required evidence artifacts.

    Returns (has_any, missing_files):
      - (True, []) if all evidence exists
      - (True, [missing]) if some evidence exists (warn but allow)
      - (False, [all_missing]) if NO evidence exists (block)
    """
    evidence_dir = project_root / ".claude" / "evidence"
    if not evidence_dir.exists():
        return False, REQUIRED_EVIDENCE

    missing = []
    found = 0
    for filename in REQUIRED_EVIDENCE:
        if (evidence_dir / filename).exists():
            found += 1
        else:
            missing.append(filename)

    if found == 0:
        return False, missing

    return True, missing


def main():
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        hook_input = {}

    agent_name = hook_input.get("agent_name", "unknown")
    if agent_name != "qa-reviewer":
        sys.exit(0)

    project_root = find_project_root()
    if project_root is None:
        sys.exit(0)

    has_any, missing = check_evidence(project_root)

    if not has_any:
        error_msg = (
            f"GOVERNANCE BLOCK: QA reviewer cannot start without evidence artifacts.\n"
            f"Missing from .claude/evidence/: {', '.join(missing)}\n"
            f"Coding agents must run quality gates and produce evidence first."
        )
        print(json.dumps({"result": "block", "reason": error_msg}))
        sys.exit(1)

    if missing:
        # Some evidence exists but not all - warn but allow
        print(
            json.dumps(
                {
                    "result": "warn",
                    "message": f"Partial evidence: missing {', '.join(missing)}. QA proceeding with available evidence.",
                }
            )
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
