# Coding Standards Quick Reference

**Purpose**: Cross-cutting coding standards loaded on-demand by coding and QA agents.
**Authoritative source**: `~/.claude/prompts/system/coding_system_prompt_v4_0_hex_tdd_8k.md`

---

## Prime Directive

> Every change must be task-scoped, atomic, deterministic, hexagonal, and evidenced.

---

## Verification Checkpoints (Non-Negotiable)

**After ANY file edit (Edit/Write tool), run verification:**

```bash
# Python projects
ruff check . && mypy . && pytest

# Frontend projects
npm run build && npm run lint

# Full-stack - run both as appropriate
```

**Checkpoint Triggers (re-read system prompt + project artifacts):**

| Trigger | Action |
|---------|--------|
| Every 15 substantive turns | Re-anchor: read rules.yaml, quality_gates.md, system prompt |
| Before starting each new task | Re-anchor + verify no blockedBy tasks |
| After error recovery (>3 turns debugging) | Re-anchor + self-audit |
| After any tangent or user question | Re-anchor before resuming |
| When tempted to say "just this once" | STOP. Re-anchor. |

**Self-Audit Questions:**
- Am I following TDD (tests before implementation)?
- Am I staying within task scope (no "while I'm here" edits)?
- Are my changes hexagonal (core depends only on ports)?
- Have I updated contracts for any changed components?
- Do evidence artifacts exist for completed work?

**Strict Prohibitions:**
- NEVER skip the verification checkpoint
- NEVER mark a task done without evidence artifacts
- NEVER continue past 40 turns without fresh conversation

---

## Layer-Specific Testing (Mandatory)

| Layer | Test Type | Coverage Requirement | Tool |
|-------|-----------|---------------------|------|
| **Domain (entities, policies)** | Unit tests | 100% of public functions | pytest |
| **Services (use cases)** | Integration tests with fakes | All happy paths + error paths | pytest |
| **Adapters (I/O)** | Contract tests | Verify port protocol compliance | pytest |
| **API Endpoints** | HTTP integration tests | All routes, all status codes | pytest + httpx |
| **UI Components** | E2E tests | Critical user flows | Playwright |

### Test Evidence Requirements

A task is **NOT COMPLETE** unless:

```
[ ] .claude/evidence/test_report.json exists
[ ] .claude/evidence/test_failures.json exists (even if empty)
[ ] .claude/evidence/quality_gates_run.json exists
[ ] All tests relevant to the task pass
[ ] New code has corresponding new tests
[ ] manifest.yaml updated with task status
```

### E2E Test Mandates (Lessons 44, 53-57)

- All interactive elements MUST have `data-testid` attributes
- Selectors: Prefer `data-testid` over CSS classes or text content
- Authentication: Create reusable auth helpers, not copy-paste login sequences
- Port conflicts: Check ports before starting test servers
- Database: Test seed scripts must match actual schema

### Contract Testing for APIs (Lessons 108, 109, 113)

Every API endpoint MUST have:
1. **Pydantic response model** - defines the contract
2. **Integration test validating ALL fields** - catches field mismatches
3. **TypeScript types generated from Pydantic** - never hand-write frontend types

### Filter Parameter Testing (Lesson 109)

Every filter/query parameter MUST have a test proving it works.

---

## Determinism Requirements (Lessons 27, 107)

### Forbidden in Core/Domain Code

| Forbidden | Reason | Alternative |
|-----------|--------|-------------|
| `datetime.now()` | Non-deterministic | Inject `TimePort` |
| `datetime.utcnow()` | Deprecated in Python 3.12 | Use `datetime.now(UTC)` via `TimePort` |
| `uuid4()` | Non-deterministic | Inject `UUIDPort` |
| `random.*` | Non-deterministic | Inject `RandomPort` |
| Module-level mutable state | Hidden coupling | Inject `StoragePort` |

### Detection Command

```bash
grep -r "datetime\.now\|datetime\.utcnow\|uuid4" src/*/core/ --include="*.py" | grep -v import
# Count MUST be zero
```

---

## Atomic Component Enforcement

Every component in `src/components/<ComponentName>/` MUST have:

| File | Purpose | Created When |
|------|---------|--------------|
| `component.py` | Pure entry point with `run()` | Before implementation |
| `models.py` | Frozen dataclass Input/Output | Before implementation |
| `ports.py` | Protocol interfaces | Before implementation |
| `contract.md` | Human-readable specification | Before implementation |
| `__init__.py` | Re-exports public API | Before implementation |

Create ALL stubs BEFORE writing implementation code.

---

## API Contract Requirements (Lessons 108-113)

- Define explicit Pydantic response model for every endpoint
- Have integration test validating ALL fields
- Log observable data flow (not silent defaults)
- Define field names in Pydantic model FIRST, then implement
- Use Protocol-based callback typing
- Run `mypy --strict` to catch signature mismatches

---

## Dependency Pinning Strategy (Lessons 2, 23)

```toml
# Pin major+minor range, document WHY
dependencies = [
    "fastapi>=0.109.0,<0.115.0",   # Pin major+minor range
    "websockets>=12.0,<14.0",      # Flet 0.28 incompatible with 14+
    "pydantic>=2.0.0,<3.0.0",      # Pin major version
]
```

After confirming working state: `pip freeze > requirements.lock`

---

## Standing Instructions

- Follow hexagonal architecture: core depends only on ports; adapters depend on core
- Use strict task loop discipline: one task at a time, TDD, evidence artifacts
- Run quality gates after every task (produce machine-readable artifacts)
- Update manifest after completing tasks or reviews
- Use drift detection - halt and create EV entries when scope changes
- Keep domain rules in YAML files, not hardcoded (rules-first execution)
- Pin dependencies appropriately based on past version issues
- Evolution and decisions logs are append-only - never rewrite history
- Never overwrite artifacts - always create new versions (v1 -> v2)
