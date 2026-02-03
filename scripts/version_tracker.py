#!/usr/bin/env python3
"""
Bi-Temporal Version Tracker for Claude Agent Framework

Tracks changes to agents, prompts, schemas, and other components with:
- Valid time: When a version was active
- Transaction time: When the change was recorded

Usage:
    ./version_tracker.py scan          # Detect and record changes
    ./version_tracker.py history       # Show change history
    ./version_tracker.py query <date>  # Show state at a point in time
    ./version_tracker.py diff <date1> <date2>  # Compare two points in time
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Resolve repo root
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
VERSIONS_DIR = REPO_ROOT / "versions"
HISTORY_FILE = VERSIONS_DIR / "history.json"

# Components to track (relative to repo root)
TRACKED_PATHS = {
    "agents": "agents",
    "prompts/system": "prompts/system",
    "prompts/playbooks": "prompts/playbooks",
    "schemas": "schemas",
    "lenses": "lenses",
    "knowledge": "knowledge",
    "docs": "docs",
}

# File extensions to track
TRACKED_EXTENSIONS = {".md", ".yaml", ".yml", ".json", ".py"}


def compute_checksum(file_path: Path) -> str:
    """Compute SHA-256 checksum of file content."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()[:16]  # Short hash for readability


def load_history() -> dict:
    """Load version history from JSON file."""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return {
        "schema_version": "1.0",
        "records": [],
        "snapshots": []
    }


def save_history(history: dict) -> None:
    """Save version history to JSON file."""
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2, default=str)


def get_current_components() -> dict:
    """Scan repo and return current state of all tracked components."""
    components = {}

    for component_type, rel_path in TRACKED_PATHS.items():
        dir_path = REPO_ROOT / rel_path
        if not dir_path.exists():
            continue

        for file_path in dir_path.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.suffix not in TRACKED_EXTENSIONS:
                continue
            if file_path.name.startswith("."):
                continue

            relative = file_path.relative_to(REPO_ROOT)
            component_name = file_path.stem

            components[str(relative)] = {
                "component_type": component_type,
                "component_name": component_name,
                "file_path": str(relative),
                "checksum": compute_checksum(file_path),
            }

    return components


def get_latest_record(history: dict, file_path: str) -> Optional[dict]:
    """Get the most recent record for a file path (where valid_to is null)."""
    for record in reversed(history["records"]):
        if record["file_path"] == file_path and record["valid_to"] is None:
            return record
    return None


def scan_changes(history: dict) -> list:
    """Compare current state against history, return list of changes."""
    current = get_current_components()
    changes = []
    now = datetime.now(timezone.utc).isoformat()

    # Track which paths we've seen
    current_paths = set(current.keys())
    historical_paths = {r["file_path"] for r in history["records"] if r["valid_to"] is None}

    # Check for new or modified files
    for file_path, component in current.items():
        latest = get_latest_record(history, file_path)

        if latest is None:
            # New file
            changes.append({
                **component,
                "version": "1.0.0",
                "valid_from": now,
                "valid_to": None,
                "recorded_at": now,
                "change_type": "initial",
                "change_summary": "Initial version",
            })
        elif latest["checksum"] != component["checksum"]:
            # Modified file - close old record and create new
            changes.append({
                "action": "close",
                "file_path": file_path,
                "valid_to": now,
            })

            # Increment version
            old_version = latest.get("version", "1.0.0")
            parts = old_version.split(".")
            parts[-1] = str(int(parts[-1]) + 1)
            new_version = ".".join(parts)

            changes.append({
                **component,
                "version": new_version,
                "valid_from": now,
                "valid_to": None,
                "recorded_at": now,
                "change_type": "modified",
                "change_summary": f"Updated (checksum changed from {latest['checksum']})",
            })

    # Check for deleted files
    for file_path in historical_paths - current_paths:
        latest = get_latest_record(history, file_path)
        if latest:
            changes.append({
                "action": "close",
                "file_path": file_path,
                "valid_to": now,
            })
            changes.append({
                **{k: latest[k] for k in ["component_type", "component_name", "file_path"]},
                "checksum": None,
                "version": latest.get("version", "1.0.0") + "-deleted",
                "valid_from": now,
                "valid_to": now,  # Immediately closed
                "recorded_at": now,
                "change_type": "deleted",
                "change_summary": "File removed",
            })

    return changes


def apply_changes(history: dict, changes: list) -> int:
    """Apply changes to history, return count of changes applied."""
    applied = 0

    for change in changes:
        if change.get("action") == "close":
            # Close existing record
            for record in history["records"]:
                if record["file_path"] == change["file_path"] and record["valid_to"] is None:
                    record["valid_to"] = change["valid_to"]
                    break
        else:
            # Add new record
            history["records"].append({k: v for k, v in change.items() if k != "action"})
            applied += 1

    return applied


def get_state_at(history: dict, target_date: datetime) -> list:
    """Get system state at a specific point in time."""
    target_iso = target_date.isoformat()
    state = []

    for record in history["records"]:
        valid_from = record["valid_from"]
        valid_to = record["valid_to"]

        # Record is valid if: valid_from <= target < valid_to (or valid_to is null)
        if valid_from <= target_iso:
            if valid_to is None or target_iso < valid_to:
                state.append(record)

    return sorted(state, key=lambda r: (r["component_type"], r["component_name"]))


def format_record(record: dict, verbose: bool = False) -> str:
    """Format a record for display."""
    name = record["component_name"]
    version = record.get("version", "?")
    change_type = record.get("change_type", "")
    checksum = record.get("checksum", "")[:8] if record.get("checksum") else "deleted"

    if verbose:
        return f"  {record['component_type']}/{name} v{version} [{checksum}] ({change_type})"
    return f"  {record['component_type']}/{name} v{version}"


def cmd_scan(args):
    """Scan for changes and record them."""
    history = load_history()
    changes = scan_changes(history)

    if not changes:
        print("No changes detected.")
        return 0

    # Filter out "close" actions for display
    new_records = [c for c in changes if c.get("action") != "close"]

    print(f"Detected {len(new_records)} change(s):\n")
    for change in new_records:
        symbol = {"initial": "+", "modified": "~", "deleted": "-"}.get(change["change_type"], "?")
        print(f"  [{symbol}] {change['component_type']}/{change['component_name']}")
        print(f"      {change['change_summary']}")

    if not args.dry_run:
        applied = apply_changes(history, changes)
        save_history(history)
        print(f"\nRecorded {applied} change(s) to {HISTORY_FILE}")
    else:
        print("\n(dry-run mode - no changes saved)")

    return 0


def cmd_history(args):
    """Show version history."""
    history = load_history()

    if not history["records"]:
        print("No history recorded yet. Run 'scan' first.")
        return 0

    # Group by component
    by_component = {}
    for record in history["records"]:
        key = f"{record['component_type']}/{record['component_name']}"
        if key not in by_component:
            by_component[key] = []
        by_component[key].append(record)

    # Filter by component type if specified
    if args.type:
        by_component = {k: v for k, v in by_component.items() if k.startswith(args.type)}

    # Show history
    for component, records in sorted(by_component.items()):
        print(f"\n{component}:")
        for record in records:
            valid_from = record["valid_from"][:10]
            valid_to = record["valid_to"][:10] if record["valid_to"] else "current"
            version = record.get("version", "?")
            change_type = record.get("change_type", "")
            print(f"  v{version} | {valid_from} → {valid_to} | {change_type}")

    return 0


def cmd_query(args):
    """Query system state at a point in time."""
    history = load_history()

    # Parse date
    try:
        if args.date.lower() == "now":
            target = datetime.now(timezone.utc)
        else:
            # Try various formats
            for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
                try:
                    target = datetime.strptime(args.date, fmt).replace(tzinfo=timezone.utc)
                    break
                except ValueError:
                    continue
            else:
                print(f"Could not parse date: {args.date}")
                print("Expected formats: YYYY-MM-DD, YYYY-MM-DDTHH:MM:SS")
                return 1
    except Exception as e:
        print(f"Error parsing date: {e}")
        return 1

    state = get_state_at(history, target)

    if not state:
        print(f"No records found for date: {args.date}")
        return 0

    print(f"System state at {target.strftime('%Y-%m-%d %H:%M:%S UTC')}:\n")

    current_type = None
    for record in state:
        if record["component_type"] != current_type:
            current_type = record["component_type"]
            print(f"\n[{current_type}]")
        print(format_record(record, verbose=args.verbose))

    print(f"\nTotal: {len(state)} components")
    return 0


def cmd_diff(args):
    """Compare system state between two dates."""
    history = load_history()

    # Parse dates
    def parse_date(date_str):
        if date_str.lower() == "now":
            return datetime.now(timezone.utc)
        for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"]:
            try:
                return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        raise ValueError(f"Could not parse date: {date_str}")

    try:
        date1 = parse_date(args.date1)
        date2 = parse_date(args.date2)
    except ValueError as e:
        print(str(e))
        return 1

    state1 = {r["file_path"]: r for r in get_state_at(history, date1)}
    state2 = {r["file_path"]: r for r in get_state_at(history, date2)}

    all_paths = set(state1.keys()) | set(state2.keys())

    added = []
    removed = []
    modified = []

    for path in all_paths:
        in_1 = path in state1
        in_2 = path in state2

        if in_2 and not in_1:
            added.append(state2[path])
        elif in_1 and not in_2:
            removed.append(state1[path])
        elif state1[path].get("checksum") != state2[path].get("checksum"):
            modified.append((state1[path], state2[path]))

    print(f"Diff: {date1.strftime('%Y-%m-%d')} → {date2.strftime('%Y-%m-%d')}\n")

    if added:
        print(f"Added ({len(added)}):")
        for r in added:
            print(f"  + {r['component_type']}/{r['component_name']}")

    if removed:
        print(f"\nRemoved ({len(removed)}):")
        for r in removed:
            print(f"  - {r['component_type']}/{r['component_name']}")

    if modified:
        print(f"\nModified ({len(modified)}):")
        for old, new in modified:
            print(f"  ~ {old['component_type']}/{old['component_name']}")
            print(f"    v{old.get('version', '?')} → v{new.get('version', '?')}")

    if not (added or removed or modified):
        print("No differences found.")

    return 0


def cmd_init(args):
    """Initialize version tracking with current state."""
    history = load_history()

    if history["records"] and not args.force:
        print("History already exists. Use --force to reinitialize.")
        return 1

    if args.force:
        history = {"schema_version": "1.0", "records": [], "snapshots": []}

    # Scan all components as initial state
    current = get_current_components()
    now = datetime.now(timezone.utc).isoformat()

    for file_path, component in current.items():
        history["records"].append({
            **component,
            "version": "1.0.0",
            "valid_from": now,
            "valid_to": None,
            "recorded_at": now,
            "change_type": "initial",
            "change_summary": "Initial tracking",
        })

    save_history(history)
    print(f"Initialized tracking for {len(current)} components.")
    print(f"History saved to: {HISTORY_FILE}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Bi-temporal version tracking for Claude Agent Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s init                    Initialize tracking with current state
  %(prog)s scan                    Detect and record changes
  %(prog)s scan --dry-run          Show changes without recording
  %(prog)s history                 Show full version history
  %(prog)s history --type agents   Show history for agents only
  %(prog)s query 2026-01-15        Show state on a specific date
  %(prog)s query now               Show current state
  %(prog)s diff 2026-01-01 now     Compare two points in time
        """
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # init command
    init_parser = subparsers.add_parser("init", help="Initialize version tracking")
    init_parser.add_argument("--force", action="store_true", help="Reinitialize even if history exists")

    # scan command
    scan_parser = subparsers.add_parser("scan", help="Scan for changes and record them")
    scan_parser.add_argument("--dry-run", action="store_true", help="Show changes without recording")

    # history command
    history_parser = subparsers.add_parser("history", help="Show version history")
    history_parser.add_argument("--type", help="Filter by component type (e.g., 'agents')")

    # query command
    query_parser = subparsers.add_parser("query", help="Query state at a point in time")
    query_parser.add_argument("date", help="Date to query (YYYY-MM-DD or 'now')")
    query_parser.add_argument("-v", "--verbose", action="store_true", help="Show more details")

    # diff command
    diff_parser = subparsers.add_parser("diff", help="Compare two points in time")
    diff_parser.add_argument("date1", help="First date (YYYY-MM-DD or 'now')")
    diff_parser.add_argument("date2", help="Second date (YYYY-MM-DD or 'now')")

    args = parser.parse_args()

    commands = {
        "init": cmd_init,
        "scan": cmd_scan,
        "history": cmd_history,
        "query": cmd_query,
        "diff": cmd_diff,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
