#!/usr/bin/env python3
"""
Governance Hook: Verify manifest was updated during the session.

Triggered by Stop hook. Checks if manifest.yaml exists and was modified
recently (within the last hour). Outputs a reminder if not.

This is a soft check (exit 0 always) - it reminds but doesn't block.
"""

import json
import sys
import time
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
    project_root = find_project_root()
    if project_root is None:
        # Not in a project - nothing to check
        sys.exit(0)

    manifest = project_root / ".claude" / "manifest.yaml"
    if not manifest.exists():
        sys.exit(0)

    # Check if manifest was modified in the last hour
    mtime = manifest.stat().st_mtime
    age_seconds = time.time() - mtime
    one_hour = 3600

    if age_seconds > one_hour:
        print(
            json.dumps(
                {
                    "result": "warn",
                    "message": (
                        "REMINDER: manifest.yaml has not been updated this session. "
                        "If you completed tasks or reviews, update the manifest before ending."
                    ),
                }
            )
        )

    # Always exit 0 - this is advisory, not blocking
    sys.exit(0)


if __name__ == "__main__":
    main()
