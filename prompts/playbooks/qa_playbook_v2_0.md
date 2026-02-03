# QA Playbook (v2.1 - Manifest-Aligned)

## Core Principles
- Use evidence artifacts first; do not rely on narrative.
- If change crosses component boundaries without BA artifact updates, flag governance failure.
- Prefer small, actionable fix lists tied to contracts and ports.
- **Read manifest first** to get correct artifact paths.

---

## Document Locations

All documents are read from `.claude/manifest.yaml`:

| Document | Manifest Key | Default Path |
|----------|--------------|--------------|
| Spec | `artifact_versions.spec.file` | `.claude/artifacts/002_spec_v{N}.md` |
| Tasklist | `artifact_versions.tasklist.file` | `.claude/artifacts/003_tasklist_v{N}.md` |
| Rules | `artifact_versions.rules.file` | `.claude/artifacts/004_rules_v{N}.yaml` |
| Quality Gates | `artifact_versions.quality_gates.file` | `.claude/artifacts/005_quality_gates_v{N}.md` |

Evidence artifacts (fixed locations):
- `.claude/evidence/quality_gates_run.json`
- `.claude/evidence/test_report.json`
- `.claude/evidence/test_failures.json`
- `.claude/evidence/lint_report.json`

---

## Review Startup Protocol

1. **Read Manifest First**
   ```
   Read: .claude/manifest.yaml
   Extract: artifact paths, phase, last_updated
   ```

2. **Check Evidence Artifacts**
   - Verify `.claude/evidence/quality_gates_run.json` exists
   - Check timestamp is recent (after latest code changes)

3. **Get Diff Context**
   - `git diff` for uncommitted changes
   - PR content if reviewing a PR

---

## ID Sequencing Protocol (MANDATORY)

Before creating ANY new BUG or IMPROVE IDs:

### Step 1: Search for Existing IDs
```bash
grep -r "BUG-[0-9]" .claude/remediation/ | sort
grep -r "IMPROVE-[0-9]" .claude/remediation/ | sort
```

### Step 2: Find Highest Numbers
- Extract the highest BUG-XXX number found
- Extract the highest IMPROVE-XXX number found

### Step 3: Increment from Highest
- New bugs start at highest + 1
- New improvements start at highest + 1

### Rules
- IDs are **project-global** (not per-review)
- IDs are **never reused** (even for resolved items)
- IDs are **sequential** (no gaps in new assignments)

### Example
```
Existing: BUG-001, BUG-002, BUG-003 (resolved), BUG-004
New bugs start at: BUG-005

Existing: IMPROVE-001, IMPROVE-002
New improvements start at: IMPROVE-003
```

---

## Output Artifacts

### Review Report
Location: `.claude/remediation/qa_YYYY-MM-DD.md`

### Remediation Tasks (Append Only)
Location: `.claude/remediation/remediation_tasks.md`

**Never overwrite existing items.** Append new findings at the end.

---

## Manifest Update (MANDATORY)

After completing review, update `.claude/manifest.yaml`:

```yaml
reviews:
  last_qa_review:
    date: "YYYY-MM-DDTHH:MM:SSZ"
    result: "PASS|PASS_WITH_NOTES|NEEDS_WORK|BLOCKED"
    report_file: ".claude/remediation/qa_YYYY-MM-DD.md"

outstanding:
  remediation:
    # Append new items (don't remove existing)
    - id: "BUG-XXX"
      source: "qa_review"
      priority: "critical|high|medium|low"
      status: "pending"
      summary: "Brief description"
      file: "affected/file.py"
      created: "YYYY-MM-DD"
```

---

## Checklist Template

### 1) Task Discipline
- [ ] Exactly one task scope (or documented multi-task rationale in EV/D)
- [ ] Task status updated correctly in tasklist
- [ ] Manifest `outstanding.tasks` reflects completion

### 2) TDD / Tests
- [ ] New behavior has tests
- [ ] Tests map to AC/TA intent
- [ ] Test files created BEFORE implementation (check timestamps)

### 3) Hexagonal Integrity
- [ ] Core does not import adapters/frameworks
- [ ] Ports are interfaces/protocols
- [ ] Adapters contain side effects

### 4) Determinism
- [ ] No time/random/global state in core
- [ ] TimePort/UUIDPort used where needed

### 5) Governance
- [ ] Drift/change recorded as EV if detected
- [ ] Task blocked appropriately if drift found

### 6) Quality Gates + Evidence
- [ ] `.claude/evidence/quality_gates_run.json` exists
- [ ] `.claude/evidence/test_report.json` exists
- [ ] Status shows PASS
- [ ] No hidden overrides without D-entry

### 7) Verification Checkpoints
- [ ] Gates run after EVERY file edit (not batched)
- [ ] Evidence of turn-based checkpoints (every 15 turns)
- [ ] No "quick fix" or "while I'm here" language
- [ ] TDD order verified (tests before implementation)

---

## Response Format

```markdown
## QA Review: YYYY-MM-DD

**Result**: PASS | PASS_WITH_NOTES | NEEDS_WORK | BLOCKED

### Summary
[1-2 sentence overall assessment]

### Findings by Section

#### 1) Task Discipline
- [PASS/FAIL] [Finding]

#### 2) TDD / Tests
- [PASS/FAIL] [Finding]

#### 3) Hexagonal Integrity
- [PASS/FAIL] [Finding]

#### 4) Determinism
- [PASS/FAIL] [Finding]

#### 5) Governance
- [PASS/FAIL] [Finding]

#### 6) Quality Gates + Evidence
- [PASS/FAIL] [Finding]

#### 7) Verification Checkpoints
- [PASS/FAIL] [Finding]

### New Bugs (if any)
- BUG-XXX: [Summary]

### New Improvements (if any)
- IMPROVE-XXX: [Summary]

### Required Fixes (if NEEDS_WORK)
1. [Fix description]
2. [Fix description]

### Evidence Paths
- `.claude/evidence/quality_gates_run.json`
- `.claude/evidence/test_report.json`
```

---

## Escalation Triggers

| Condition | Escalate To |
|-----------|-------------|
| Spec ambiguity | BA Agent |
| Missing AC/TA | BA Agent |
| Architectural violation | Solution Designer |
| Security gap | Solution Designer |
| Recurring pattern (3+) | Lessons Advisor |
| Preventable failure | Lessons Advisor |
