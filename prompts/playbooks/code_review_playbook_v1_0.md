# Code Review Playbook (v1.0)

## When to Use Code Review Agent vs QA Reviewer

| Scenario | Use |
|----------|-----|
| Quick governance check | QA Reviewer |
| PR with simple changes | QA Reviewer |
| Task marked complete, need verification | Code Review Agent |
| Complex feature implementation | Code Review Agent |
| Bug fix needs root cause analysis | Code Review Agent |
| Pre-release quality gate | Code Review Agent |

## Review Session Structure (60 min)

### Phase 1: Context (5 min)
```bash
# Gather inputs
1. Read task from tasklist (identify task ID)
2. Extract referenced stories, ACs, TAs
3. List changed files: git diff --name-only
4. Locate evidence artifacts
```

### Phase 2: Prime Directive (10 min)

Run each check systematically:

**Task-Scoped Check:**
```bash
# Compare changed files to task scope
git diff --name-only | while read f; do
  # Is this file related to task?
  grep -l "task-relevant-term" "$f" || echo "WARN: $f may be out of scope"
done
```

**Deterministic Check:**
```bash
# Search for time/random violations in core
grep -rn "datetime.now\|datetime.utcnow\|random\." src/components/*/component.py
# Should return empty; any hit is a violation
```

**Hexagonal Check:**
```bash
# Check core imports
grep -rn "^from src.components.*/adapters" src/components/*/component.py
grep -rn "^import requests\|^import sqlite3\|^import os" src/components/*/component.py
# Should return empty; any hit is a violation
```

### Phase 3: Task Completion (15 min)

**Story Tracing Template:**
```markdown
## US-XXX: [Story Title]

Actor: [Who]
Action: [What they do]
Goal: [Why]

Implementation Trace:
- Entry point: [file:line or "MISSING"]
- Action handler: [file:line or "MISSING"]
- Goal achievable: [YES/NO/PARTIAL]

Gaps: [List any missing functionality]
```

**AC-Test Mapping Template:**
```markdown
## AC-XXX: [Criterion]

Test Location: [file:line or "MISSING"]
Test Validates AC: [YES/NO/PARTIAL]

Assertions checked:
- [ ] Happy path
- [ ] Error case 1: [description]
- [ ] Error case 2: [description]
- [ ] Boundary: [description]

Gaps: [Missing coverage]
```

### Phase 4: Code Quality (15 min)

**Structural Checklist (per component):**
```
src/components/{Name}/
├── component.py    [ ] exists [ ] has run() [ ] pure (no side effects)
├── models.py       [ ] exists [ ] Input dataclass [ ] Output dataclass
├── ports.py        [ ] exists [ ] Protocols defined [ ] used in component
├── contract.md     [ ] exists [ ] matches implementation
├── __init__.py     [ ] exists [ ] re-exports public API
└── tests/          [ ] exists [ ] has unit tests [ ] has contract test
```

**Implementation Quick Scan:**
```python
# Red flags to search for:
grep -rn "TODO\|FIXME\|HACK\|XXX" src/  # Unresolved work
grep -rn "except:$\|except Exception:" src/  # Overly broad catches
grep -rn "pass$" src/components/*/component.py  # Empty implementations
grep -rn "print(" src/components/  # Debug statements left in
```

**Test Quality Quick Scan:**
```python
# Weak test patterns:
grep -rn "assert True\|assert 1" tests/  # Always-passing tests
grep -rn "def test_.*:$" tests/ -A 5 | grep -B 5 "pass$"  # Empty tests
```

### Phase 5: Documentation (15 min)

**Bug Report Template:**
```markdown
## BUG-XXX: [Short title]

**Severity:** [Critical|High|Medium|Low]
**Category:** [Logic|Security|Performance|UX|Governance]

### Evidence
- File: `path/to/file.py:42`
- Code: `problematic_code_snippet()`
- Expected: [What should happen]
- Actual: [What happens]

### Root Cause
[Why did this happen?]
- [ ] Missing test
- [ ] Spec ambiguity
- [ ] Implementation error
- [ ] Integration issue

### Fix
\```python
# Before
problematic_code()

# After
fixed_code()
\```

### Prevention (for Lessons Advisor)
[How to prevent this class of bug]
- New gate check?
- Prompt update?
- Checklist item?

### Refs
- Task: T-XXX
- Story: US-XXX
- AC: AC-XXX
```

**Improvement Report Template:**
```markdown
## IMPROVE-XXX: [Short title]

**Priority:** [Should|Could|Won't]
**Type:** [Refactor|Pattern|Performance|Readability|Testability]

### Current State
[What exists now]

### Proposed
[What would be better]

### Why
- Benefit 1
- Benefit 2
- Trade-off consideration

### Sketch
\```python
# Improved approach
\```

### Effort
- Files: N
- Risk: [Low|Medium|High]
- Prerequisites: [Any blockers]

### Decision
[ ] Proceed (add to tasklist as T-XXX)
[ ] Defer (add to tech debt backlog)
[ ] Reject (reason: ___)
```

## Machine-Readable Output

Always produce `artifacts/code_review_summary.json`:

```json
{
  "task_id": "T-XXX",
  "timestamp": "2026-01-19T10:30:00Z",
  "status": "NEEDS_WORK",
  "prime_directive": {
    "task_scoped": "pass",
    "atomic": "pass",
    "deterministic": "fail",
    "hexagonal": "pass",
    "evidenced": "pass"
  },
  "completion_verification": {
    "user_stories": [
      {"id": "US-012", "status": "complete"},
      {"id": "US-013", "status": "partial", "gap": "cookie removal not tested"}
    ],
    "acceptance_criteria": [
      {"id": "AC-012.1", "test_exists": true, "test_valid": true},
      {"id": "AC-012.2", "test_exists": true, "test_valid": false, "gap": "missing rate limit check"},
      {"id": "AC-013.1", "test_exists": true, "test_valid": false, "gap": "cookie not verified"}
    ]
  },
  "bugs": [
    {"id": "BUG-001", "severity": "medium", "file": "component.py", "line": 47, "category": "determinism"}
  ],
  "improvements": [
    {"id": "IMPROVE-001", "priority": "should", "type": "testability"}
  ],
  "blocking_issues": ["BUG-001 must be fixed before PASS"]
}
```

## Common Failure Patterns (What to Watch For)

### Pattern 1: "Works on my machine" determinism
```
Symptom: Test passes locally, fails in CI
Check: datetime.now(), file paths, environment variables in core
Fix: Inject via ports
```

### Pattern 2: Test exists but doesn't validate
```
Symptom: AC has matching test but test is trivial
Check: Does assertion actually verify the AC?
Fix: Strengthen assertion, add edge cases
```

### Pattern 3: Scope creep via "improvements"
```
Symptom: Files changed that aren't in task scope
Check: Compare diff to task definition
Fix: Revert out-of-scope changes, create separate task
```

### Pattern 4: Missing error path tests
```
Symptom: Happy path works, errors unhandled
Check: Are error cases from AC tested?
Fix: Add explicit error tests
```

### Pattern 5: Contract drift
```
Symptom: contract.md doesn't match implementation
Check: Compare contract to actual component signature
Fix: Update contract OR fix implementation to match
```

## Integration Points

### Handing Off to Coding Agent (NEEDS_WORK)
```markdown
## Required Fixes for T-XXX

The following must be addressed before re-review:

1. [ ] BUG-001: Replace datetime.now() with injected TimePort
   - File: src/components/Auth/component.py:47
   - Reference: Prime Directive #3 (Determinism)

2. [ ] Missing test for AC-012.2 rate limiting
   - Create: tests/unit/test_auth_rate_limit.py
   - Must verify: 3 failed attempts triggers lockout

Re-run quality gates after fixes. Re-submit for review.
```

### Handing Off to Lessons Advisor (Patterns Found)
```markdown
## Patterns for Lessons Advisor

Recurring issue detected (3+ occurrences):

**Pattern:** datetime.now() in component core
**Occurrences:** Auth, Scheduler, Notification components
**Root cause:** No gate checking for time calls in core

**Proposed Prevention:**
- Add to quality gates: grep check for datetime.now in component.py
- Add to coding prompt: "datetime.now() is NEVER allowed in component.py"
- Add to checklist: "Verify time injection via TimePort"
```

## Quick Reference

```
Phase 1 (5 min):  Read task, stories, ACs → list files → find artifacts
Phase 2 (10 min): Run 5 Prime Directive checks
Phase 3 (15 min): Trace stories → map ACs to tests → verify spec fidelity
Phase 4 (15 min): Check structure → scan implementation → evaluate tests
Phase 5 (15 min): Document bugs → document improvements → write summary
```
