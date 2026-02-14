#!/usr/bin/env python3
"""
Governance Hook: Block deployment commands unless ops gate exists.

Triggered by PreToolUse for Bash tool calls (matcher: "Bash").
Checks if the command matches deployment patterns and blocks if no valid gate.

Exit codes:
  0 = command allowed
  2 = deployment blocked (no valid gate)
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

DEPLOY_PATTERNS = [
    r"\bfly\s+deploy\b",
    r"\bflyctl\s+deploy\b",
    r"\bfly\s+apps\s+(create|destroy|restart|move)\b",
    r"\bfly\s+scale\b",
    r"\bfly\s+secrets\s+(set|unset|import)\b",
    r"\bfly\s+machine\s+(start|stop|restart|update|run|destroy)\b",
    r"\bfly\s+volumes\s+(create|destroy|extend|fork)\b",
    r"\bfly\s+postgres\b",
    r"\bgh\s+workflow\s+run\b",
    r"\bgh\s+run\s+rerun\b",
    r"\.deploy_gate",  # Block attempts to write gate file via bash
]

GATE_TTL_SECONDS = 600  # 10 minutes


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


def matches_deployment_pattern(command: str) -> bool:
    """Check if a command matches any deployment pattern."""
    for pattern in DEPLOY_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False


def gate_is_valid(gate_file: Path) -> bool:
    """Check if gate file exists and is within TTL."""
    if not gate_file.exists():
        return False
    try:
        gate_data = json.loads(gate_file.read_text())
        created_at = datetime.fromisoformat(gate_data["created_at"])
        age = (datetime.now(timezone.utc) - created_at).total_seconds()
        return age < GATE_TTL_SECONDS
    except (json.JSONDecodeError, KeyError, ValueError):
        return False


def main():
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        hook_input = {}

    tool_input = hook_input.get("tool_input", {})
    command = tool_input.get("command", "")

    if not matches_deployment_pattern(command):
        sys.exit(0)

    project_root = find_project_root()
    if project_root is None:
        # No project context - still block deployment commands as a safety net
        print(
            json.dumps(
                {
                    "result": "block",
                    "reason": (
                        "DEPLOYMENT BLOCKED: Only ops can execute deployments. "
                        "No project context found. Launch ops via Task tool."
                    ),
                }
            )
        )
        sys.exit(2)

    gate_file = project_root / ".claude" / ".deploy_gate"

    if gate_is_valid(gate_file):
        sys.exit(0)

    print(
        json.dumps(
            {
                "result": "block",
                "reason": (
                    "DEPLOYMENT BLOCKED: Only ops can execute deployments.\n"
                    "Launch ops via Task tool to perform deployments.\n"
                    "Read-only commands (fly status, fly logs, etc.) are not affected."
                ),
            }
        )
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
