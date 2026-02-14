---
name: drift
description: "Detect drift between architectural decisions and actual code"
user_invocable: true
---

# /drift — Decisions-vs-Code Drift Detection

Verify that architectural decisions (ADRs) are actually reflected in the codebase.

## Steps

1. Find the project root by locating `.claude/manifest.yaml` in the current directory or parents.

2. Check for `.claude/drift_rules.yaml`:
   - If **missing**, offer to create a template:
     ```bash
     cd ~/Developer/claude-agent-framework && python -m claude_cli.main drift init --project-root <project_root>
     ```
   - Then help the user fill in rules based on their `decisions.md` or ADRs.

3. Run drift detection:
   ```bash
   cd ~/Developer/claude-agent-framework && python -m claude_cli.main drift check --project-root <project_root>
   ```

4. Display results:
   - Show each decision and its assertion results (PASS/FAIL)
   - Highlight any drift found

5. If drift is found, suggest remediation:
   - For code drift: suggest code changes to re-align with the decision
   - For stale decisions: suggest updating the ADR if the decision has evolved

6. Optionally save a report to `.claude/evidence/`:
   ```bash
   cd ~/Developer/claude-agent-framework && python -m claude_cli.main drift report --project-root <project_root>
   ```

## Assertion Types

- `grep_exists` — Pattern MUST match at least once in path
- `grep_absent` — Pattern MUST NOT match in path
- `file_exists` — Path must exist
- `file_absent` — Path must not exist

## Notes

- Drift rules live at `{project}/.claude/drift_rules.yaml`
- Each rule maps to an architectural decision (ADR)
- The engine uses grep (subprocess) and pathlib for checks
- Reports can be saved as both JSON and Markdown
