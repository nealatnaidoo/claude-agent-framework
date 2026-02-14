#!/usr/bin/env python3
"""
Governance Hook: Verify agent matches current manifest phase.

Triggered by SubagentStart hook for all workflow agents.
Blocks agent start if the current phase doesn't match the agent's expected phase.

Exit codes:
  0 = phase matches (or not in a project context)
  1 = phase mismatch, block agent start
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Which agents are allowed in which phases
PHASE_AGENT_MAP = {
    "initialized": ["init", "persona"],
    "solution_design": ["design", "lessons"],
    "ba": ["ba", "lessons"],
    "coding": [
        "back",
        "front",
        "lessons",
        "qa",
    ],
    "fast_track": [
        "back",
        "front",
        "qa",
    ],
    "qa": ["qa"],
    "code_review": ["review"],
    "remediation": [
        "back",
        "front",
    ],
    "complete": ["ops"],
    "paused": [],
}

# Agents that can run in ANY phase (not phase-restricted)
UNRESTRICTED_AGENTS = [
    "ops",
    "audit",
    "lessons",
    "init",
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


def read_phase(project_root: Path) -> str | None:
    """Read the phase field from manifest.yaml."""
    manifest = project_root / ".claude" / "manifest.yaml"
    if not manifest.exists():
        return None

    # Simple YAML parsing for phase field (avoid external deps)
    for line in manifest.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("phase:"):
            value = stripped.split(":", 1)[1].strip().strip("\"'")
            return value
    return None


def main():
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        hook_input = {}

    agent_name = hook_input.get("agent_name", "unknown")

    # Unrestricted agents can run anywhere
    if agent_name in UNRESTRICTED_AGENTS:
        sys.exit(0)

    project_root = find_project_root()
    if project_root is None:
        # No manifest found — check for lost_lamb exception
        claude_dir = find_claude_dir()
        if claude_dir and check_lost_lamb(claude_dir):
            sys.exit(0)  # Valid exception, allow
        # No manifest and no valid exception — block
        error_msg = (
            f"GOVERNANCE BLOCK: {agent_name} cannot run without a project manifest.\n"
            "No .claude/manifest.yaml found in any parent directory.\n"
            "\n"
            "Options:\n"
            "  1. Run init to scaffold governance\n"
            "  2. Use /lost-lamb for a 24hr ad-hoc exception\n"
            "  3. Use /broken-arrow to retrofit governance on an existing project"
        )
        print(json.dumps({"result": "block", "reason": error_msg}))
        sys.exit(1)

    phase = read_phase(project_root)
    if phase is None:
        # No phase set - allow (might be initializing)
        sys.exit(0)

    # Check if agent is allowed in current phase
    allowed_agents = PHASE_AGENT_MAP.get(phase, [])
    if agent_name in allowed_agents:
        sys.exit(0)

    # Phase mismatch - block
    error_msg = (
        f"PHASE MISMATCH: {agent_name} cannot run during '{phase}' phase.\n"
        f"Allowed agents for '{phase}': {', '.join(allowed_agents) or '(none)'}\n"
        f"Update manifest phase or invoke the correct agent for this phase."
    )
    print(json.dumps({"result": "block", "reason": error_msg}))
    sys.exit(1)


if __name__ == "__main__":
    main()
