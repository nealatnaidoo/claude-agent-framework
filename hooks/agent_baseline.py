#!/usr/bin/env python3
"""
Agent Baseline Manager - Detects contamination in agent prompts.

Maintains SHA-256 hashes of agent files to detect unauthorized modifications.
Used by startup_check.py to verify agent integrity before each session.

Usage:
    python agent_baseline.py create    # Create/update baseline
    python agent_baseline.py verify    # Verify against baseline
    python agent_baseline.py status    # Show baseline status
"""

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

# Paths
AGENTS_DIR = Path.home() / ".claude" / "agents"
BASELINE_FILE = Path.home() / ".claude" / ".agent_baseline.json"

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def hash_file(filepath: Path) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_agent_files() -> list[Path]:
    """Get all agent markdown files."""
    if not AGENTS_DIR.exists():
        return []
    return sorted(AGENTS_DIR.glob("*.md"))


def create_baseline() -> dict:
    """Create baseline hashes for all agent files."""
    agents = get_agent_files()

    baseline = {
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat(),
        "agents": {}
    }

    for agent_path in agents:
        baseline["agents"][agent_path.name] = {
            "hash": hash_file(agent_path),
            "size": agent_path.stat().st_size,
            "mtime": agent_path.stat().st_mtime,
        }

    # Save baseline
    BASELINE_FILE.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_FILE.write_text(json.dumps(baseline, indent=2))

    return baseline


def load_baseline() -> dict | None:
    """Load existing baseline."""
    if not BASELINE_FILE.exists():
        return None
    try:
        return json.loads(BASELINE_FILE.read_text())
    except (json.JSONDecodeError, IOError):
        return None


def verify_baseline() -> dict:
    """
    Verify current agents against baseline.

    Returns dict with:
        - verified: bool - all agents match baseline
        - baseline_exists: bool - baseline file exists
        - baseline_date: str - when baseline was created
        - agent_count: int - number of agents checked
        - changes: list - list of changed/new/removed agents
        - details: dict - per-agent verification results
    """
    result = {
        "verified": False,
        "baseline_exists": False,
        "baseline_date": None,
        "agent_count": 0,
        "changes": [],
        "details": {},
    }

    baseline = load_baseline()
    if not baseline:
        result["changes"].append({"type": "no_baseline", "message": "No baseline exists"})
        return result

    result["baseline_exists"] = True
    result["baseline_date"] = baseline.get("updated", baseline.get("created"))

    current_agents = {p.name: p for p in get_agent_files()}
    baseline_agents = baseline.get("agents", {})

    all_agent_names = set(current_agents.keys()) | set(baseline_agents.keys())
    result["agent_count"] = len(current_agents)

    for name in sorted(all_agent_names):
        if name not in current_agents:
            # Agent was removed
            result["changes"].append({
                "type": "removed",
                "agent": name,
                "message": f"Agent removed: {name}"
            })
            result["details"][name] = {"status": "removed"}

        elif name not in baseline_agents:
            # New agent added
            result["changes"].append({
                "type": "added",
                "agent": name,
                "message": f"New agent: {name}"
            })
            result["details"][name] = {"status": "added"}

        else:
            # Check if modified
            current_hash = hash_file(current_agents[name])
            baseline_hash = baseline_agents[name]["hash"]

            if current_hash != baseline_hash:
                result["changes"].append({
                    "type": "modified",
                    "agent": name,
                    "message": f"Agent modified: {name}"
                })
                result["details"][name] = {
                    "status": "modified",
                    "baseline_hash": baseline_hash[:12],
                    "current_hash": current_hash[:12],
                }
            else:
                result["details"][name] = {"status": "verified"}

    # Verified if no changes detected
    result["verified"] = len(result["changes"]) == 0

    return result


def print_status():
    """Print baseline status."""
    baseline = load_baseline()

    if not baseline:
        print(f"{YELLOW}No baseline exists.{RESET}")
        print(f"Run: python agent_baseline.py create")
        return

    print(f"{BOLD}Agent Baseline Status{RESET}")
    print(f"{'='*50}")
    print(f"Created: {baseline.get('created', 'unknown')}")
    print(f"Updated: {baseline.get('updated', 'unknown')}")
    print(f"Agents:  {len(baseline.get('agents', {}))}")
    print()

    # Verify current state
    result = verify_baseline()

    if result["verified"]:
        print(f"{GREEN}Status: VERIFIED - No changes detected{RESET}")
    else:
        print(f"{RED}Status: CHANGES DETECTED{RESET}")
        for change in result["changes"]:
            icon = {"added": "+", "removed": "-", "modified": "~"}.get(change["type"], "?")
            color = {"added": CYAN, "removed": RED, "modified": YELLOW}.get(change["type"], "")
            print(f"  {color}{icon} {change['message']}{RESET}")


def print_create_result(baseline: dict):
    """Print result of baseline creation."""
    agent_count = len(baseline.get("agents", {}))
    print(f"{GREEN}Baseline created successfully{RESET}")
    print(f"  Agents: {agent_count}")
    print(f"  File: {BASELINE_FILE}")
    print(f"  Time: {baseline['created']}")


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python agent_baseline.py [create|verify|status]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "create":
        baseline = create_baseline()
        print_create_result(baseline)

    elif command == "verify":
        result = verify_baseline()
        if result["verified"]:
            print(f"{GREEN}VERIFIED{RESET}: All {result['agent_count']} agents match baseline")
            sys.exit(0)
        else:
            print(f"{RED}FAILED{RESET}: Changes detected")
            for change in result["changes"]:
                print(f"  - {change['message']}")
            sys.exit(1)

    elif command == "status":
        print_status()

    else:
        print(f"Unknown command: {command}")
        print("Usage: python agent_baseline.py [create|verify|status]")
        sys.exit(1)


if __name__ == "__main__":
    main()
