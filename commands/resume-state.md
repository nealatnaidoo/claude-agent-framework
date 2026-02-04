---
allowed-tools: Read, Glob, Bash(pwd), Bash(date:*), Bash(git:*)
description: Resume work from a saved session state
---

## Context

- Current directory: !`pwd`
- Timestamp: !`date +"%Y-%m-%d %H:%M:%S"`
- Git branch: !`git branch --show-current 2>/dev/null || echo "not a git repo"`

## Your Task

Read the saved session state from `.claude/session_state.md` and prepare to resume work.

**User's notes (optional):** `$ARGUMENTS`

### Instructions

1. **Read the state file** - Load `.claude/session_state.md`
2. **Summarize for the user**:
   - Original intent
   - What was completed
   - What was in progress
   - Next planned actions
3. **Check current state**:
   - Are the mentioned files still present?
   - Has the git branch changed?
   - Any obvious changes since state was saved?
4. **Propose resumption** - Suggest how to continue

### If State File Missing

If `.claude/session_state.md` doesn't exist:
1. Check for `.claude/manifest.yaml` as alternative context
2. Check git log for recent commits that might provide context
3. Ask user what they'd like to work on

### Output Format

Present the loaded state clearly:

```
## Resuming Session

**Last saved**: <timestamp from file>
**Original goal**: <brief summary>

### Completed
- Item 1
- Item 2

### Was In Progress
<what was being worked on>

### Next Actions
1. Action 1
2. Action 2

### Ready to Continue?

I'll start with: <first next action>

Type 'go' to continue, or provide different instructions.
```

### Rules

- **Read before acting** - Don't start work until user confirms
- Present state **concisely** - User should quickly understand where we left off
- Note any **discrepancies** - If files are missing or branch changed, mention it
- If user provided notes, incorporate them into the resumption plan

### After Reading

Wait for user confirmation before proceeding with the next actions.
