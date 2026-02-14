#!/usr/bin/env python3
"""
Governance Hook: Protect .lost_lamb file from direct Write/Edit.

Triggered by PreToolUse for Write and Edit tool calls (matcher: "Write|Edit").
The .lost_lamb exception file should only be managed by the /lost-lamb command via Bash.

Exit codes:
  0 = not touching .lost_lamb file, allow
  2 = blocked attempt to write .lost_lamb file
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

    if ".lost_lamb" in file_path:
        print(
            json.dumps(
                {
                    "result": "block",
                    "reason": (
                        "BLOCKED: .lost_lamb is managed by the /lost-lamb command. "
                        "Use /lost-lamb to create a 24hr governance exception."
                    ),
                }
            )
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
