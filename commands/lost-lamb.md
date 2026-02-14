---
allowed-tools: Read, Bash(pwd), Bash(date:*), Bash(mkdir:*), Bash(python3:*)
description: Create a 24hr governance exception for ad-hoc work without a manifest
---

## Context

- Current directory: !`pwd`
- Timestamp: !`date -u +"%Y-%m-%dT%H:%M:%SZ"`

## Your Task

Create a temporary 24hr governance exception (`.claude/.lost_lamb`) so agents can run in a directory without a full manifest. This is for **urgent or ad-hoc work only** — not a substitute for proper governance.

**User's reason (optional):** `$ARGUMENTS`

### Instructions

1. **Check if manifest already exists**
   - Look for `.claude/manifest.yaml` in the current directory tree
   - If found, tell the user: "A manifest already exists — you don't need a lost-lamb exception. Your agents should work normally."
   - Stop here if manifest exists

2. **Get a reason**
   - If `$ARGUMENTS` is provided, use it as the reason
   - If not, ask the user why they need the exception (one sentence is fine)

3. **Check for existing exception**
   - If `.claude/.lost_lamb` already exists and is still valid (created < 24h ago), report the existing exception details and remaining time
   - Ask the user if they want to replace it or keep the existing one

4. **Create the exception file**
   - Create `.claude/` directory if it doesn't exist: `mkdir -p .claude`
   - Use Bash with python3 to write the file (NOT the Write tool — it would be blocked by protect_lost_lamb.py):
   ```bash
   python3 -c "
   import json
   from datetime import datetime, timezone, timedelta
   now = datetime.now(timezone.utc)
   expires = now + timedelta(hours=24)
   data = {
       'created_at': now.strftime('%Y-%m-%dT%H:%M:%SZ'),
       'reason': '<USER_REASON>',
       'expires_at': expires.strftime('%Y-%m-%dT%H:%M:%SZ')
   }
   with open('.claude/.lost_lamb', 'w') as f:
       json.dump(data, f, indent=2)
   print(json.dumps(data, indent=2))
   "
   ```
   - Replace `<USER_REASON>` with the actual reason

5. **Report back** with:
   - Confirmation the exception was created
   - File location (absolute path)
   - Expiry time (24h from now)
   - Reminder: "This is a temporary measure. Run `init` or `/broken-arrow` to set up proper governance before the exception expires."

### Rules

- NEVER use the Write or Edit tool to create `.lost_lamb` — the protect_lost_lamb.py hook will block it
- Always use Bash with python3 to write the file
- The exception lasts exactly 24 hours from creation
- Do not create the exception if a manifest already exists
