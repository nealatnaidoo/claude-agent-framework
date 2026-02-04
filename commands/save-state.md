---
allowed-tools: Read, Write, Bash(date:*), Bash(git:*)
description: Save conversation progress, intent, and next actions for session resumption
---

## Context

- Current directory: !`pwd`
- Timestamp: !`date +"%Y-%m-%d %H:%M:%S"`
- Git branch: !`git branch --show-current 2>/dev/null || echo "not a git repo"`
- Git status: !`git status --porcelain 2>/dev/null | head -10`

## Your Task

Save the current session state to `.claude/session_state.md` so work can be resumed after a restart.

**User's notes (optional):** `$ARGUMENTS`

### Instructions

1. **Analyze the conversation** - Review what has been discussed and accomplished
2. **Identify the current state**:
   - What was the original request/goal?
   - What has been completed so far?
   - What is currently in progress?
   - What are the next planned actions?
   - Are there any blockers or pending decisions?
3. **Write state file** - Save to `.claude/session_state.md` in the current project

### State File Format

Write the file with this structure:

```markdown
# Session State

**Saved**: <timestamp>
**Branch**: <git branch>
**Project**: <current directory name>

## Original Intent

<What the user originally asked for - the main goal>

## Completed Work

<Bulleted list of what has been done>
- Item 1
- Item 2

## In Progress

<What was being worked on when state was saved>

## Next Actions

<Ordered list of what should happen next>
1. Action 1
2. Action 2
3. Action 3

## Context & Decisions

<Important context, decisions made, or constraints discovered>

## Files Modified

<List of files that were created or modified this session>

## Blockers / Pending

<Any blockers, questions, or items waiting on user input>

## User Notes

<Any notes the user provided with the save command>
```

### Rules

- Be **specific** about what was done and what's next
- Include **file paths** where relevant
- Capture **decisions made** so they don't need to be re-discussed
- If user provided notes with the command, include them in User Notes section
- Create `.claude/` directory if it doesn't exist

### After Saving

Report back with:
- Confirmation the state was saved
- Summary of next actions (so user knows what to expect on resume)
