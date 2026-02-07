#!/usr/bin/env python3
"""
Governance Hook: Protect .deploy_gate file from direct Write/Edit.

Triggered by PreToolUse for Write and Edit tool calls (matcher: "Write|Edit").
The gate file should only be managed by manage_deploy_gate.py via SubagentStart.

Exit codes:
  0 = not touching gate file, allow
  2 = blocked attempt to write gate file
"""

import json
import sys


def main():
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        hook_input = {}

    tool_input = hook_input.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if ".deploy_gate" in file_path:
        print(
            json.dumps(
                {
                    "result": "block",
                    "reason": (
                        "BLOCKED: .deploy_gate is managed by the deployment gate hook. "
                        "Use devops-governor agent for deployments."
                    ),
                }
            )
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
