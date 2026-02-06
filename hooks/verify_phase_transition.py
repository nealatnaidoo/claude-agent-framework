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
from pathlib import Path

# Which agents are allowed in which phases
PHASE_AGENT_MAP = {
    "initialized": ["project-initializer", "persona-evaluator"],
    "solution_design": ["solution-designer", "lessons-advisor"],
    "ba": ["business-analyst", "lessons-advisor"],
    "coding": [
        "backend-coding-agent",
        "frontend-coding-agent",
        "lessons-advisor",
    ],
    "fast_track": [
        "backend-coding-agent",
        "frontend-coding-agent",
    ],
    "qa": ["qa-reviewer"],
    "code_review": ["code-review-agent"],
    "remediation": [
        "backend-coding-agent",
        "frontend-coding-agent",
    ],
    "complete": ["devops-governor"],
    "paused": [],
}

# Agents that can run in ANY phase (not phase-restricted)
UNRESTRICTED_AGENTS = [
    "devops-governor",
    "compliance-verifier",
    "lessons-advisor",
    "project-initializer",
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
        # Not in a project context - allow
        sys.exit(0)

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
