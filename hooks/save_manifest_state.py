#!/usr/bin/env python3
"""
Governance Hook: Save manifest state before context compression.

Triggered by PreCompact hook. Ensures the manifest reflects current state
before context is compressed, so the agent can recover cleanly.

Creates a timestamped backup of the manifest alongside the original.
"""

import json
import shutil
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
    project_root = find_project_root()
    if project_root is None:
        sys.exit(0)

    manifest = project_root / ".claude" / "manifest.yaml"
    if not manifest.exists():
        sys.exit(0)

    # Create timestamped backup
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup = manifest.parent / f"manifest_backup_{timestamp}.yaml"
    shutil.copy2(manifest, backup)

    # Keep only the 3 most recent backups
    backups = sorted(manifest.parent.glob("manifest_backup_*.yaml"), reverse=True)
    for old_backup in backups[3:]:
        old_backup.unlink()

    print(
        json.dumps(
            {
                "result": "info",
                "message": f"Manifest backed up to {backup.name} before compaction.",
            }
        )
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
