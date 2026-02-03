---
allowed-tools: Read, Edit, Bash(grep:*)
description: Capture a learning from the current session and append to devlessons.md
---

## Context

- Current directory: !`pwd`
- Today's date: !`date +%Y-%m-%d`
- Current lesson count: !`grep -c "^### Lesson:" /Users/naidooone/Developer/claude/prompts/devlessons.md 2>/dev/null || echo "0"`

## Your Task

Capture a lesson from the current conversation and append it to `/Users/naidooone/Developer/claude/prompts/devlessons.md`.

**User's input:** `$ARGUMENTS`

### Instructions

1. **Analyze the conversation** - Find the key learning, problem, and solution discussed
2. **Determine the lesson** - What went wrong? What was the fix? What should be done differently next time?
3. **Append to devlessons.md** - Add a new lesson entry at the END of the file (before the `## Summary` section if it exists, or at the very end)

### Lesson Format

Use this exact format:

```markdown
---

### Lesson: <concise title>

**What happened (<project name>, <date>):**

<1-2 paragraphs describing the problem or discovery>

**The fix:**

<code blocks or steps showing the solution>

### Future Checklist:
- [ ] <actionable item 1>
- [ ] <actionable item 2>
- [ ] <actionable item 3>
```

### Rules

- Keep lessons **concise** - focus on the actionable takeaway
- Include **code examples** when relevant
- Make checklist items **specific and actionable**
- If user provides a topic/title, use it; otherwise infer from conversation
- Do NOT update the table of contents (it's manually curated)
- Append BEFORE the `## Summary: Top 30 Rules` section if it exists

### After Adding

Report back with:
- The lesson title added
- The key takeaway in one sentence
