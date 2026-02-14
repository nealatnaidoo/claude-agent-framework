#!/usr/bin/env python3
"""
Advisory Hook: Validate YAML files after Write/Edit operations.

Triggered by PostToolUse for Write|Edit tool calls.
Checks if the written/edited file is YAML and validates it parses correctly.

Exit codes:
  0 = file is valid YAML or not a YAML file (always passes)

Output: Advisory warning via JSON if YAML is malformed.
"""

import json
import sys
from pathlib import Path


def main():
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})

    # Get the file path from the tool input
    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)

    # Only check YAML files
    path = Path(file_path)
    if path.suffix.lower() not in (".yaml", ".yml"):
        sys.exit(0)

    if not path.exists():
        sys.exit(0)

    # Try to parse the YAML
    try:
        import yaml

        content = path.read_text()
        yaml.safe_load(content)
        # Valid YAML - no output needed
        sys.exit(0)
    except ImportError:
        # yaml module not available - skip validation silently
        sys.exit(0)
    except yaml.YAMLError as e:
        # Invalid YAML - emit advisory warning
        print(
            json.dumps(
                {
                    "result": "warn",
                    "message": f"YAML validation warning: {path.name} contains invalid YAML.\n{e}",
                }
            )
        )
        sys.exit(0)
    except Exception:
        # Any other error - don't block
        sys.exit(0)


if __name__ == "__main__":
    main()
