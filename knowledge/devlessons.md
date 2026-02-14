# Development Lessons Learned

**Project**: Little Research Lab + dbxloader (Databricks POC) + Matrix Risk Engine + Agentic HUD Extension
**Date**: 2026-02-04 (updated with agent CLI tools architecture lesson 118)
**Purpose**: Capture hard-won lessons to inform future projects and avoid repeating mistakes.

---

## Table of Contents
1. [Framework Selection](#1-framework-selection)
2. [Version Pinning & Dependencies](#2-version-pinning--dependencies)
3. [Fly.io Deployment](#3-flyio-deployment)
4. [Architecture Decisions](#4-architecture-decisions)
5. [Quality Gates & TDD](#5-quality-gates--tdd)
6. [Project Structure](#6-project-structure)
7. [Process & Governance](#7-process--governance)
8. [Atomic Component Pattern Enforcement](#8-atomic-component-pattern-enforcement)
9. [Complete Migrations & Split-Brain Prevention](#9-complete-migrations--preventing-split-brain-architecture)
10. [Deprecation Strategy & Technical Debt](#10-deprecation-strategy--technical-debt-paydown)
11. [Manifest & Tasklist Synchronization](#11-manifest--tasklist-synchronization)
12. [Completing Architectural Migrations](#12-completing-architectural-migrations)
13. [Deterministic Core & Dependency Injection](#13-deterministic-core--dependency-injection)
14. [_impl.py Re-export Pattern](#14-_implpy-re-export-pattern)
15. [Python Keyword as Module Name](#15-python-keyword-as-module-name)
16. [Sitemap Filtering Semantics](#16-sitemap-filtering-semantics)
17. [Cache Header Configuration Location](#17-cache-header-configuration-location)
18. [Radix UI Select Empty Value Constraint](#18-radix-ui-select-empty-value-constraint)
19. [MCP Server & FastMCP Architecture Patterns](#19-mcp-server--fastmcp-architecture-patterns)
20. [Token Efficiency in MCP Tool Responses](#20-token-efficiency-in-mcp-tool-responses)
21. [Provider Fallback Architecture](#21-provider-fallback-architecture)
22. [MCP Tool Response Time](#22-mcp-tool-response-time)
23. [Claude Desktop MCP Configuration](#23-claude-desktop-mcp-configuration)
24. [Atomic Component Pattern for MCP Adapters](#24-atomic-component-pattern-for-mcp-adapters)
25. [Solution Designer → BA → Coding Agent Workflow](#25-solution-designer--ba--coding-agent-workflow)
26. [tiktoken for Accurate Token Estimation](#26-tiktoken-for-accurate-token-estimation)
27. [datetime.utcnow() Deprecation](#27-datetimeutcnow-deprecation)
28. [Claude Code Permissions Configuration](#28-claude-code-permissions-configuration)
29. [Claude Code Directory Access Permissions](#29-claude-code-directory-access-permissions)
30. [Quality Adapters for MCP Integration](#30-quality-adapters-for-mcp-integration)
31. [Governance Drift via Atomic Component Drift](#31-governance-drift-via-atomic-component-drift)
32. [Browser Automation with Playwright](#32-browser-automation-with-playwright)
33. [Selector Versioning for Dynamic Web Apps](#33-selector-versioning-for-dynamic-web-apps)
34. [Hardcoded Paths in Development Code](#34-hardcoded-paths-in-development-code)
35. [QA Remediation Session Analysis & Drift Detection Metrics](#35-qa-remediation-session-analysis--drift-detection-metrics)
36. [Quality Gates Artifacts File Size Limits](#lesson-36-quality-gates-artifacts-file-size-limits)
37. [BA Artifacts May Be Gitignored](#lesson-37-ba-artifacts-may-be-gitignored---check-before-committing)
38. [TipTap Custom Extension Pattern for Rich Attributes](#lesson-38-tiptap-custom-extension-pattern-for-rich-attributes)
39. [shadcn/ui Component Dependencies](#lesson-39-shadcnui-component-dependencies-must-be-added-incrementally)
40. [Image Placement Architecture](#lesson-40-image-placement-architecture---storing-metadata-in-tiptap-nodes)
41. [Prompt Library CRUD Pattern](#lesson-41-prompt-library-crud-pattern---browsedetailadmin-architecture)
42. [TipTap Content Rendering Pipeline](#lesson-42-tiptap-content-rendering-pipeline---separating-special-nodes)
43. [OpenGraph Metadata Extraction from TipTap](#lesson-43-opengraph-metadata-extraction-from-tiptap-json)
44. [E2E Test Patterns for Feature Workflows](#lesson-44-e2e-test-patterns-for-feature-workflows)
45. [Security Audit Test Patterns](#lesson-45-security-audit-test-patterns)
46. [Placement-Specific CSS Architecture](#lesson-46-placement-specific-css-architecture)
47. [Test Doubles Must Match Production Adapter Signatures](#lesson-47-test-doubles-must-match-production-adapter-signatures)
48. [Integration Test Database Schemas Must Be Complete](#lesson-48-integration-test-database-schemas-must-be-complete)
49. [Mock Patch Paths Must Match Post-Refactor Module Locations](#lesson-49-mock-patch-paths-must-match-post-refactor-module-locations)
50. [Use Specific Exception Types in pytest.raises](#lesson-50-use-specific-exception-types-in-pytestraises)
51. [Quality Gates Should Exclude Unimplemented Feature Tests](#lesson-51-quality-gates-should-exclude-unimplemented-feature-tests)
52. [Configuration Paths Must Be Consistent Across Codebase](#lesson-52-configuration-paths-must-be-consistent-across-codebase)
53. [E2E Test Selectors Must Match Actual DOM Attributes](#lesson-53-e2e-test-selectors-must-match-actual-dom-attributes)
54. [Test Database Seed Scripts Must Match Actual Schema](#lesson-54-test-database-seed-scripts-must-match-actual-schema)
55. [Check Port Conflicts Before Starting Local Servers](#lesson-55-check-port-conflicts-before-starting-local-servers)
56. [Playwright Config Must Match Running Server Ports](#lesson-56-playwright-config-must-match-running-server-ports)
57. [E2E Tests Need Authentication Helpers for Reuse](#lesson-57-e2e-tests-need-authentication-helpers-for-reuse)
58. [Pydantic Literal Types Must Be Consistent Across All Schema Files](#lesson-58-pydantic-literal-types-must-be-consistent-across-all-schema-files)
59. [Next.js "use client" Directive Affects All Exports](#lesson-59-nextjs-use-client-directive-affects-all-exports)
60. [Realistic Test Data Exposes Type Validation Issues](#lesson-60-realistic-test-data-exposes-type-validation-issues)
61. [E2E Tests Creating Dynamic Content May Fail in Production Mode](#lesson-61-e2e-tests-creating-dynamic-content-may-fail-in-production-mode)
62. [Database Tables Must Exist for All Features Being Tested](#lesson-62-database-tables-must-exist-for-all-features-being-tested)
63-75. *(See lessons in document body)*
76. [Background Subagents Cannot Prompt for Bash Permissions](#lesson-76-background-subagents-cannot-prompt-for-bash-permissions)
77. [Token Validation Must Use Constant-Time Comparison](#lesson-77-token-validation-must-use-constant-time-comparison)
78. [Environment Variables Should Be Optional for Testing](#lesson-78-environment-variables-should-be-optional-for-testing)
79. [Atomic Components Require contract.md Files](#lesson-79-atomic-components-require-contractmd-files)
80. [MyPy Requires Explicit None Checks for Optional Types](#lesson-80-mypy-requires-explicit-none-checks-for-optional-types)
81. [React setState in useEffect Should Use useMemo for Derived State](#lesson-81-react-setstate-in-useeffect-should-use-usememo-for-derived-state)
82. [Skipped Test Files Still Need Valid Python Syntax](#lesson-82-skipped-test-files-still-need-valid-python-syntax)
83. [Clarify Data Location Before Debugging "Missing" Content](#lesson-83-clarify-data-location-before-debugging-missing-content)
84. [Database Overrides for YAML-Defined Configuration](#lesson-84-database-overrides-for-yaml-defined-configuration)
85. [Next.js Static Generation Timeouts for Demo Pages](#lesson-85-nextjs-static-generation-timeouts-for-demo-pages)
86. [Role-Based Profile Display Requires Correct Role Assignment](#lesson-86-role-based-profile-display-requires-correct-role-assignment)
87. [Prime Directive Compliance Remediation (TimePort, EnvConfigPort)](#lesson-87-prime-directive-compliance-remediation-timeport-envconfigport)
88. [Unity Catalog Volumes When DBFS Public Access Disabled](#lesson-88-unity-catalog-volumes-required-when-dbfs-public-access-disabled)
89. [Schema Type Mismatch INT vs BIGINT](#lesson-89-schema-type-mismatch-int-vs-bigint-from-spark-sql-introspection)
90. [Decimal Precision Consistency](#lesson-90-decimal-precision-must-be-consistent-across-config-and-table-schema)
91. [Null Checking with filter() Expression](#lesson-91-null-checking-in-arrays-must-use-filter-expression)
92. [Widget Defaults Must Match File Names](#lesson-92-widget-defaults-must-match-actual-file-names-in-volume)
93. [Databricks Serverless Compute Only](#lesson-93-databricks-workspace-may-only-support-serverless-compute)
94. [Explicit Boolean Validation Columns](#lesson-94-validation-logic-needs-explicit-boolean-columns)
95. [Config-Driven Data Loading Pattern](#lesson-95-config-driven-data-loading-pattern-for-databricks)
96. [Stress Test P&L Calculation - Weight Normalization](#lesson-96-stress-test-pl-calculation---weight-normalization-required)
97. [Functional Validation Over Unit Test Coverage](#lesson-97-functional-validation-over-unit-test-coverage)
98. [Module Import in Scripts Directory](#lesson-98-module-import-in-scripts-directory)
99. [VaR Model Validation - Kupiec POF Test](#lesson-99-var-model-validation---kupiec-pof-test)
100. [Hexagonal Architecture for External C++ Libraries](#lesson-100-hexagonal-architecture-for-external-c-libraries)
101. [Parallel Agent Execution for Large Feature Implementation](#lesson-101-parallel-agent-execution-for-large-feature-implementation)
102. [Solution Designer → BA → Coding Agent Pipeline](#lesson-102-solution-designer--ba--coding-agent-pipeline)
103. [Extension Pattern - Extend Don't Modify Core](#lesson-103-extension-pattern---extend-dont-modify-core)
104. [MCP Tool Token Budget Enforcement](#lesson-104-mcp-tool-token-budget-enforcement)
105. [Composite Health Score Design Pattern](#lesson-105-composite-health-score-design-pattern)
106. [Documentation System Integration Pattern](#lesson-106-documentation-system-integration-pattern)
107. [Centralize Time & UUID Port Definitions to Prevent Determinism Violations](#lesson-107-centralize-time--uuid-port-definitions-to-prevent-determinism-violations)
108. [API Response Contracts Must Be Validated at Integration Points](#lesson-108-api-response-contracts-must-be-validated-at-integration-points)
109. [Filter Parameters Require Type-Checked Function Signatures](#lesson-109-filter-parameters-require-type-checked-function-signatures)
110. [Defensive Coding Without Observability Hides Data Flow Bugs](#lesson-110-defensive-coding-without-observability-hides-data-flow-bugs)
111. [Business Logic Duplication Creates Divergence Risk](#lesson-111-business-logic-duplication-creates-divergence-risk)
112. [UI Controls Without Backend Integration Tests Are Dead Code](#lesson-112-ui-controls-without-backend-integration-tests-are-dead-code)
113. [Runtime Contract Validation for Dynamic API Responses](#lesson-113-runtime-contract-validation-for-dynamic-api-responses)
114. [Claude Code Subagent Types Are System-Defined](#lesson-114-claude-code-subagent-types-are-system-defined)
115. [Fly.io Dev/Prod CI/CD Pipeline Pattern](#lesson-115-flyio-devprod-cicd-pipeline-pattern)
116. [Multiple Database Files - Verify Which Database the Backend Uses](#lesson-116-multiple-database-files---verify-which-database-the-backend-uses)
117. [D2 Diagram-as-Code for Architecture Documentation](#lesson-117-d2-diagram-as-code-for-architecture-documentation)
118. [Agent CLI Tools Architecture - Scripts vs Packages](#lesson-118-agent-cli-tools-architecture---scripts-vs-packages)

---

## Topic Index

Quick lookup by technology or category:

| Topic | Lessons |
|-------|---------|
| **Risk Engine/Finance** | 96, 97, 99 |
| **Databricks** | 88, 89, 90, 91, 92, 93, 94, 95 |
| **Spark/PySpark** | 89, 90, 91, 94 |
| **Schema/Types** | 89, 90, 108, 113 |
| **Validation** | 91, 94, 108, 113 |
| **File Handling** | 88, 92 |
| **Infrastructure** | 88, 93 |
| **Architecture Patterns** | 95, 107, 111 |
| **MCP/Claude** | 19, 20, 21, 22, 23, 24, 30, 104 |
| **Agentic Development** | 25, 101, 102 |
| **Documentation** | 106, 117 |
| **Diagramming/D2** | 117 |
| **Testing** | 44, 45, 47, 48, 49, 50, 51, 53, 54, 55, 56, 57, 60, 61, 62, 76, 78, 82, 97, 99, 108, 109, 112 |
| **React/Next.js** | 18, 38, 39, 40, 41, 42, 43, 59, 81, 85 |
| **Python** | 14, 15, 27, 50, 80, 82, 98 |
| **Fly.io/Deployment** | 3 (section), 115 |
| **CI/CD** | 115 |
| **Quality Gates** | 5 (section), 36, 51 |
| **Hexagonal/Architecture** | 4 (section), 8, 9, 10, 12, 13, 24, 31, 79, 87, 100, 103, 107 |
| **Metrics/Health** | 105 |
| **Configuration** | 17, 28, 29, 34, 52, 84 |
| **API Design** | 108, 109, 113 |
| **Observability** | 110 |
| **Business Logic** | 111 |
| **Dashboard/UI** | 112 |

---

## 1. Framework Selection

### Lesson: Evaluate framework maturity before committing

**What happened:**
We chose Flet (Python→Flutter Web) because it allowed Python-only development. However, we encountered:

| Issue | Impact |
|-------|--------|
| WebSocket "Receive loop error: 'text'" | Required pinning `websockets<14.0` |
| `ft.animation.Animation` vs `ft.Animation` | API changes between minor versions |
| `DatePicker.pick_date()` doesn't exist in 0.28.x | Had to use `.open = True` instead |
| Small community | Limited Stack Overflow answers, few examples |
| Testing Flet views is non-trivial | Could not apply strict TDD to UI layer |

**Resolution:** Migrated to React/Next.js (D-0005, EV-0004).

### Future Checklist:
- [ ] Check GitHub issues for recurring compatibility complaints
- [ ] Verify the framework has stable APIs (check breaking changes in changelog)
- [ ] Confirm testing story is well-documented
- [ ] Assess community size (Stack Overflow questions, Discord activity)
- [ ] For web apps, prefer industry-standard stacks (React, Vue, etc.) unless there's a compelling reason
- [ ] "Python everywhere" is appealing but may not be worth framework immaturity

---

## 2. Version Pinning & Dependencies

### Lesson: Pin ALL transitive dependencies that can break your framework

**What happened:**
Flet 0.28.x broke with `websockets>=14.0`, `starlette>=0.40`, and various FastAPI versions. We had to discover these incompatibilities through runtime errors.

**Solution in pyproject.toml:**
```toml
# BAD - too loose
dependencies = ["flet>=0.25.0"]

# GOOD - pin the ecosystem
dependencies = [
    "flet>=0.25.0,<0.30.0",
    "websockets>=12.0,<14.0",      # Pin to avoid API changes
    "starlette>=0.36.0,<0.40.0",   # Pin for Flet compatibility
    "fastapi>=0.109.0,<0.112.0",   # Pin for starlette compatibility
    "uvicorn>=0.27.0,<0.35.0",     # Pin for Flet compatibility
]
```

### Future Checklist:
- [ ] When using a framework, check its dependencies and pin compatible ranges
- [ ] Create a `requirements.lock` or use `pip freeze` after a working state
- [ ] Document WHY each pin exists (comments in pyproject.toml)
- [ ] Test with `pip install --upgrade` periodically to catch breaking changes early
- [ ] Consider using `uv` or `poetry` for stricter dependency resolution

---

## 3. Fly.io Deployment

### Lesson: Understand Fly.io's architecture before deploying

**Issues encountered and solutions:**

### 3.1 Persistent Storage
```toml
# fly.toml - Mount a volume for SQLite and file uploads
[[mounts]]
  source = "lrl_data"
  destination = "/data"

# CRITICAL: Create volume BEFORE first deploy
# fly volumes create lrl_data --size 1 --region iad
```

**Lesson:** Without persistent storage, SQLite data and uploads are lost on every deploy.

### 3.2 PYTHONPATH Issues
```toml
# fly.toml
[env]
  PYTHONPATH = "/app"

# Dockerfile
ENV PYTHONPATH=/app
```

**Lesson:** Container structure requires explicit PYTHONPATH for module imports.

### 3.3 Health Checks Must Work
```toml
[[http_service.checks]]
  interval = "30s"
  timeout = "5s"
  grace_period = "10s"
  method = "GET"
  path = "/"
```

**Lesson:** If health check fails, Fly.io won't route traffic. Ensure "/" returns 200.

### 3.4 Build Dependencies
```dockerfile
# Dockerfile - README.md required for pip install with pyproject.toml
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir .
```

**Lesson:** If `pyproject.toml` references `readme = "README.md"`, the file must exist during build.

### 3.5 Machine Sizing
```toml
[[vm]]
  memory = "512mb"    # Minimum for Python web apps
  cpu_kind = "shared"
  cpus = 1
```

**Lesson:** 256mb is often insufficient for Python apps with dependencies like matplotlib.

### 3.6 Auto-stop/start Behavior
```toml
[http_service]
  auto_stop_machines = "stop"
  auto_start_machines = true
  min_machines_running = 0
```

**Lesson:** With `min_machines_running = 0`, first request after idle has cold start latency (~5-10s). Set to 1 for production if latency matters.

### Future Checklist:
- [ ] Create volume before first deploy
- [ ] Test Dockerfile locally with `docker build` before `fly deploy`
- [ ] Verify health check endpoint works
- [ ] Set appropriate memory (512mb+ for Python)
- [ ] Decide on cold start tolerance
- [ ] Use `fly logs` immediately after deploy to catch startup errors

---

## 4. Architecture Decisions

### Lesson: Clean architecture pays dividends during migrations

**What worked well:**

The Ports & Adapters (Hexagonal) architecture allowed us to:
1. Keep ALL domain logic unchanged during Flet→React migration
2. Keep ALL services unchanged (ContentService, AssetService, PublishService)
3. Only replace the "shell" (UI layer)

```
src/
├── domain/       # Pure Python, no I/O - UNCHANGED
├── services/     # Business logic - UNCHANGED
├── ports/        # Interfaces - UNCHANGED
├── adapters/     # SQLite, filesystem - UNCHANGED
├── app_shell/    # Flet UI - REPLACED with FastAPI routes
└── ui/           # Flet components - REPLACED with React
```

### Future Checklist:
- [ ] Separate domain logic from I/O from the start
- [ ] Use dependency injection (ports/adapters pattern)
- [ ] Test domain logic independently of UI
- [ ] Consider: "If I had to swap the UI framework, what would change?"

---

## 5. Quality Gates & TDD

### Lesson: Run quality gates after EVERY task, not just at the end

**What happened (EV-0003):**
Type checking was deferred until audit. Found 45+ mypy errors accumulated over many tasks.

**Resolution:** Enforce quality gates after each task:
```bash
python scripts/run_quality_gates.py
# Must pass before marking task "done"
```

### Lesson: Accept different testing strategies for different layers

**What happened (EV-0001):**
Tried to apply strict TDD to Flet UI views. This was impractical because:
- Flet views require runtime to test
- Event handlers are difficult to unit test
- Visual verification is often the real test

**Resolution:** Adopt layered testing strategy:

| Layer | Testing Approach |
|-------|------------------|
| Domain (entities, policies) | Unit tests, property tests (Hypothesis) |
| Services | Integration tests with fakes |
| API endpoints | HTTP integration tests |
| UI components | Manual verification + smoke tests |

### Future Checklist:
- [ ] Run quality gates (lint, types, tests) after EVERY task
- [ ] Define appropriate testing strategy per layer upfront
- [ ] Don't let type errors accumulate - fix immediately
- [ ] "Manual verification with evidence" is acceptable for UI

---

## 6. Project Structure

### Lesson: Use a consistent, documented structure from day one

**What worked:**
```
project/
├── src/                    # Application code
│   ├── domain/             # Entities, policies (pure)
│   ├── services/           # Use cases
│   ├── ports/              # Interfaces
│   ├── adapters/           # Implementations
│   └── api/                # REST endpoints
├── tests/
│   ├── unit/               # Fast, isolated tests
│   ├── integration/        # Service + adapter tests
│   └── security/           # Auth, validation tests
├── migrations/             # Database migrations
├── scripts/                # Dev utilities
├── artifacts/              # Quality gate outputs
└── {project}_*.md          # BA artifacts (spec, tasklist, etc.)
```

### Lesson: BA artifacts prevent scope creep

Having explicit files for spec, tasklist, decisions, evolution, and quality gates:
- Forced explicit decision-making
- Created audit trail
- Enabled "drift detection" when implementation diverged from plan
- Made handoffs between sessions possible

### Future Checklist:
- [ ] Create BA artifacts (spec, tasklist, rules, quality_gates) before coding
- [ ] Use evolution.md to track discoveries that change scope
- [ ] Use decisions.md to record architectural choices with rationale
- [ ] Keep artifacts updated - they're living documents

---

## 7. Process & Governance

### Lesson: Task discipline prevents chaos

**What worked:**
- One task at a time
- Mark `in_progress` before starting
- Mark `done` only when quality gates pass
- No "while I'm here" edits

**What we learned about task states:**
```
todo → in_progress → done     # Happy path
todo → blocked                # Missing dependency
in_progress → blocked         # Discovered issue (requires EV entry)
blocked → todo                # After BA updates artifacts
```

### Lesson: Drift detection saves rework

When implementation diverges from plan:
1. HALT coding
2. Create EV (evolution) entry
3. Update spec/rules/tasklist
4. THEN resume

This prevented us from building features that weren't specified and catching architectural issues early.

### Future Checklist:
- [ ] Use task discipline (one at a time, status tracking)
- [ ] Create EV entries for any scope/architecture changes
- [ ] Don't code through ambiguity - clarify first
- [ ] Evidence artifacts prove completion

---

## 8. Atomic Component Pattern Enforcement

### Lesson: Read the coding playbook BEFORE writing code, not after

**What happened (Remediation 2026-01-12):**

The Little Research Lab project had 11 components but only 36% compliance with atomic component standard (v3). Root cause: code was written before reading `universal_coding_agent_playbook.md`. The implementation used class-based services in `src/core/services/` instead of atomic components in `src/components/` with `run()` entry points.

**Symptoms of this mistake:**
- Components scattered across `services/`, `handlers/`, and `utils/` instead of `src/components/{ComponentName}/`
- No `run()` entry points - logic buried in class methods
- No frozen dataclass models for inputs/outputs
- No `ports.py` Protocol definitions
- No `contract.md` documentation
- Manifest showed components as "planned" but code was in wrong locations

**The fix required 3 phases:**
1. **Phase 1:** Fix type/lint errors (5 files) - legacy code had accumulated issues
2. **Phase 2:** Migrate to atomic structure (11 components, 58 files, 6,340 lines):
   - `component.py` - functional entry point with `run()` signature
   - `models.py` - frozen dataclass inputs/outputs
   - `ports.py` - Protocol interfaces for dependencies
   - `contract.md` - human-readable contract documentation
3. **Phase 3:** Update evolution log (EV-0001) and manifest

**Time cost:** ~4 hours to remediate what could have been correct in 15 minutes upfront.

### Future Checklist:
- [ ] **BEFORE first coding line:** Read `universal_coding_agent_playbook.md` Section 2 (Component Structure)
- [ ] **BEFORE first component:** Create stub with minimal `component.py`, `models.py`, `ports.py`, `contract.md`
- [ ] **Create component contract.md first**, then implement `run()` to match it (TDD-style)
- [ ] **Every task completion:** Verify component structure matches standard
- [ ] **Weekly QA reviews during development:** Don't wait until end-of-project audit

---

### Lesson: Component contracts must exist BEFORE implementation

**What happened:**
Nine of the 11 components had no `contract.md` at all. Implementation decisions were made without explicit documentation of:
- What the component does
- What inputs it accepts
- What outputs it produces
- What dependencies (ports) it requires
- What could go wrong (error cases)

This led to:
- Inconsistent error handling patterns
- Unclear component responsibilities (some did too much)
- No way to review components during code review (what was the intent?)

**The lesson:**
Use contract.md as a **specification document**, not a post-implementation artifact:

```markdown
# ComponentName Contract

## Purpose
[What does this component do? One sentence.]

## Input (RunRequest)
[Frozen dataclass with all required inputs]

## Output (RunResponse)
[Frozen dataclass with all outputs]

## Ports (Dependencies)
[List Protocol interfaces]

## Error Cases
[What can fail and how?]
```

Writing this contract BEFORE code reveals:
- Overly complex input models (reduce scope)
- Missing dependency (add to ports)
- Overlapping responsibilities (split into 2 components)

### Future Checklist:
- [ ] Create `contract.md` and get it reviewed BEFORE writing `component.py`
- [ ] Component contract is the spec for TDD tests
- [ ] If contract changes during implementation, that's an EV entry (scope discovery)
- [ ] Contract.md is referenced in code review: "Does implementation match contract?"

---

### Lesson: Atomic component drift happens silently - audit early and often

**What happened:**
Without periodic QA checks, the project accumulated drift across all 11 components:
- Some had proper `models.py`, others inlined type hints
- Some had `ports.py`, others hardcoded dependencies
- Some had tests, others had none
- Manifest was never updated when components moved

The 36% compliance score was a surprise at the end instead of a gradually identified problem.

**Why drift occurs:**
1. Familiar patterns feel faster ("I'll do a quick class-based service")
2. No immediate feedback ("That still worked")
3. Justifications accumulate ("This one is special", "We'll refactor later")
4. By phase 3, fixing is harder (more components to refactor)

**The prevention strategy:**
Create a compliance checker that runs with quality gates and fails the task if compliance drops:

```python
# scripts/check_atomic_compliance.py
# Verifies each component in src/components/{Name}/ has:
# - component.py with run() function
# - models.py with Input/Output dataclasses
# - ports.py with Protocol definitions
# - contract.md
# - At least one test file
#
# Task FAILS if any component is non-compliant
```

### Future Checklist:
- [ ] Create `check_atomic_compliance.py` in project (or use from template)
- [ ] Add to `run_quality_gates.py` - fail the build if any component is non-compliant
- [ ] **Run compliance check after EVERY task** - not just at end-of-phase audits
- [ ] Track compliance trend: target 100%, alert if drops below 95%
- [ ] Fix compliance issues immediately (before moving to next task)

---

### Lesson: TDD applied to component contracts prevents scope drift

**What happened:**
Components were written without tests-first discipline. Some components grew to handle multiple responsibilities because their scope wasn't pinned down by tests.

**The lesson:**
Test-driven development applied to **component contracts** catches scope issues early:

```python
# tests/unit/components/MyComponent_test.py

def test_component_contract_signature():
    """Component must have this exact input/output signature"""
    from src.components.MyComponent.component import run
    from src.components.MyComponent.models import Input, Output

    # MUST accept Input dataclass
    result = run(Input(field1="value"))

    # MUST return Output dataclass
    assert isinstance(result, Output)

def test_happy_path():
    """When X happens, component outputs Y"""
    # This test is written from the contract.md

def test_error_cases():
    """When Z happens, component raises CustomException"""
    # These tests come from contract.md "Error Cases" section
```

The discipline:
1. Write `contract.md` (the spec)
2. Write tests that verify the contract
3. Write `component.py` to pass the tests
4. If you want to change contract, update contract.md + tests + code together

### Future Checklist:
- [ ] Create test file at the same time as contract.md
- [ ] Test file references contract.md line numbers: "Per contract, should handle X case"
- [ ] All tests written before implementation starts
- [ ] If implementation reveals missing cases in contract, EV entry is created
- [ ] Code review includes: "Does implementation match contract AND tests?"

---

### Remediation Statistics (2026-01-12)

| Metric | Value |
|--------|-------|
| Components migrated | 11 |
| Python files created | 58 |
| Lines of component code | 6,340 |
| Contract files created | 11 |
| Tests before | 1,004 |
| Tests after | 1,265 |
| Compliance before | 36% |
| Compliance after | ~95% |

**Evidence:** `little-research-lab/RETROSPECTIVE_2026-01-12.md`, `EV-0001`

---

## 9. Complete Migrations & Preventing Split-Brain Architecture

### Lesson: Incomplete migrations create split-brain state - audit ALL code locations before declaring "done"

**What happened (Follow-up Assessment 2026-01-12):**

Initial remediation migrated 11 components to atomic pattern but left 5 components in `src/services/`:
- auth, collab, invite, publish, bootstrap
- These were in a different directory than the 11 migrated components (`src/services/` vs `src/core/services/`)
- This created a "hybrid state" with code in both `src/components/` AND `src/services/`
- Tasklist still referenced `core/services/` paths after migration

**Symptoms of split-brain state:**
- Multiple implementations of the same concept (some atomic, some not)
- Imports can resolve from both old and new locations
- Tasklist/manifest out of sync with actual code locations
- New developers don't know which version to use

**Root cause analysis:**
1. Initial scope was incomplete - only identified 11 of 16 service-like components
2. Different naming conventions hid the gap (`src/core/services/` vs `src/services/`)
3. No comprehensive audit upfront
4. Tasklist wasn't validated against all code locations

**The fix required:**
1. Comprehensive inventory of ALL components across entire codebase
2. Unified migration plan with CURRENT locations
3. ONE target location for ALL components (`src/components/`)
4. Deprecation markers with clear sunset date

### Future Checklist:
- [ ] **Before migration:** Grep entire codebase for service-like classes
- [ ] **Create inventory:** For each: current location, name, purpose
- [ ] **One migration plan:** Single source of truth for what needs to move
- [ ] **Verify complete:** No active imports from old location remain
- [ ] **External QA review:** Have someone unfamiliar verify all code is in expected location

---

### Lesson: Split-brain architectures are discovered by external review, not internal checks

**What happened:**

The initial remediation team didn't catch the missing 5 components. An external QA agent running independent assessment identified the "hybrid state":
- Manifest showed components but only 11 existed in `src/components/`
- Tasklist had old paths but code was in different locations
- Import statements mixed both old and new locations

**Why internal checks missed it:**
1. All tests passed (legacy code still works)
2. No mypy/lint errors (both locations syntactically valid)
3. "Code still works" bias - if imports resolve, the split is invisible

**Why external review caught it:**
1. Fresh eyes with no context of "what we changed"
2. Systematic check: "Where should component X be?" vs "Does our change work?"
3. Cross-referenced manifest against actual filesystem

### Future Checklist:
- [ ] **Before migration:** Document target architecture explicitly
- [ ] **After migration:** Schedule external QA review with explicit checklist
- [ ] **External reviewer validates:**
  - [ ] All manifest items exist in documented location
  - [ ] No duplicate code in old locations (or marked DEPRECATED)
  - [ ] Import statements point to new locations

---

## 10. Deprecation Strategy & Technical Debt Paydown

### Lesson: Deprecate with sunset dates, not indefinitely

**What happened:**

After migrating components, old code remained in `src/services/`. Decision was to deprecate rather than delete because:
- Some imports might still reference old locations
- Unknown external dependencies
- Gradual migration safer than big bang

But deprecation without sunset date becomes permanent technical debt.

**The trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| Delete immediately | Clean slate | Risk breaking unknown imports |
| Deprecate indefinitely | Safe | Technical debt grows forever |
| Deprecate with sunset | Clarity, eventual cleanup | Requires discipline |

**The lesson:**

```markdown
# DEPRECATED.md - src/services/

**Status:** DEPRECATED as of 2026-01-12
**Replacement:** Use `src/components/{ComponentName}/`
**Sunset Date:** 2026-02-15

After sunset, this directory will be removed.
```

### Future Checklist:
- [ ] **Create DEPRECATED.md** with migration instructions
- [ ] **Add deprecation warning to code** - `warnings.warn()`
- [ ] **Set specific sunset date** - Not "eventually", e.g., 30 days out
- [ ] **Before sunset:** Final audit for remaining imports
- [ ] **After sunset:** Delete without mercy

---

### Lesson: Use import warnings for gradual migrations

**What happened:**

After creating DEPRECATED.md, no automated warning if developers used old imports. Code silently worked from old locations.

**The solution:**

```python
# src/services/__init__.py
import warnings

warnings.warn(
    "src.services is deprecated. Use src.components instead. "
    "Sunset date: 2026-02-15",
    DeprecationWarning,
    stacklevel=2
)
```

This way:
- Developers get immediate feedback when using old location
- Tests catch the warning
- Clear migration path in the warning message

---

## 11. Manifest & Tasklist Synchronization

### Lesson: Manifest and Tasklist paths are part of Definition of Done

**What happened:**

Tasklist still referenced `core/services/` paths after migration:
- 15 references pointed to old locations
- Tasks marked "done" but documented paths were wrong
- Manifest was out of sync with actual code locations

**Why it happened:**
1. Tasklist update was delayed - coded first, updated artifacts after
2. No validation step for path accuracy
3. Task completion wasn't verified against manifest

**The lesson:**

BA artifacts are part of "definition of done":

```
Task.done criteria:
- [ ] Code written and tested
- [ ] Quality gates pass
- [ ] Tasklist/manifest paths match actual code locations
- [ ] Contract.md reflects final implementation
```

If tasklist says `src/components/Auth/` but code is at `src/services/auth.py`, task is NOT done.

### Future Checklist:
- [ ] **Before creating components:** Update manifest with target location
- [ ] **After creating components:** Update tasklist paths to match
- [ ] **Quality gate includes:** Verify no stale paths in tasklist/manifest
- [ ] **Code review includes:** "Do artifact paths match code locations?"

---

### Follow-Up Statistics (2026-01-12)

| Metric | Value |
|--------|-------|
| Additional components migrated | 5 |
| New Python files created | 25 |
| Tasklist paths updated | 15 |
| Total components now | 16 |
| Quality gates | ALL PASS |

**Evidence:** External QA assessment, follow-up remediation

---

## 12. Completing Architectural Migrations

### Lesson: Complete ALL layers in architectural migrations - never leave split implementations

**What happened (EV-0002 - Shell Layer Migration):**

After remediating domain layer components to atomic pattern (EV-0001), the shell layer was left partially unmigrated:

| Issue | Count | Impact |
|-------|-------|--------|
| Files still importing from `src.core.services` | 36 | Legacy imports preventing migration completion |
| Mypy type checking errors | 61 | Incomplete type coverage in migrated files |
| Ruff lint violations | 58 | Style/import inconsistencies |
| Compliance level | 68% | Shell layer not fully atomic |

**Root cause:** Migration was planned as "refactor components" but shell layer updates weren't explicit. Quality gates passed even with mixed imports because both old and new paths resolved.

### The 4-phase solution that worked:

**Phase 1: Create Migration Map (DEPRECATED.md)**
- Document old location → new location mappings
- Set sunset date for old imports
- Include code examples of old vs new patterns

**Phase 2: Copy Legacy Code to _impl.py Files**
- Preserves functionality while migrating structure
- Less risky than rewriting
- Allows gradual refactoring of contents later

**Phase 3: Update ALL Shell Layer Imports**
- Systematically find/replace old imports in: `src/api/routes/*.py`, `src/api/deps.py`, `src/shell/hooks/*.py`
- Verify with `grep -r "from src.core.services" src/` returns no matches

**Phase 4: Fix Quality Gate Failures**
- Resolve mypy errors from incomplete typing
- Fix ruff violations
- Create ServiceContext stubs for backward compatibility if needed

### Remediation Statistics (EV-0002)

| Metric | Value |
|--------|-------|
| Shell layer files migrated | 36 |
| Mypy errors fixed | 61 → 0 |
| Ruff violations fixed | 58 → 0 |
| Backward compatibility stubs | 5 |
| Quality gates | ALL PASS |

### Future Checklist:
- [ ] Create explicit migration map (DEPRECATED.md) BEFORE starting
- [ ] Map ALL layers: domain, services, shell, tests
- [ ] Use _impl.py as temporary stepping stone (not permanent)
- [ ] Grep for old imports to verify zero remain
- [ ] Add migration-specific quality gates to CI
- [ ] Set sunset date for _impl.py files and backward compat stubs

**Evidence:** EV-0002 resolution in little-research-lab-v3_evolution.md

---

## 13. Deterministic Core & Dependency Injection

### Lesson: Time I/O in components violates determinism - always inject TimePort

**What happened (QA Audit 2026-01-12):**

A comprehensive QA audit found 13 violations of determinism across 4 components:
- `auth/component.py` - 4 calls to `datetime.utcnow()`
- `invite/component.py` - 3 calls to `datetime.utcnow()`
- `collab/component.py` - 2 calls to `datetime.utcnow()`
- `bootstrap/component.py` - 4 calls to `datetime.now()`

**Why this matters:**
- Components become non-deterministic (same input → different output)
- Testing requires mocking `datetime` module (brittle)
- Time zone bugs become hard to reproduce
- Violates functional core / imperative shell pattern

**The fix:**

```python
# ports.py
class TimePort(Protocol):
    def now_utc(self) -> datetime: ...

# component.py
def run_create_session(
    inp: CreateSessionInput,
    time: TimePort,  # Injected dependency
) -> AuthOutput:
    now = time.now_utc()  # Not datetime.utcnow()
    ...
```

### Future Checklist:
- [ ] **Before coding:** Add TimePort to any component that needs current time
- [ ] **Grep for violations:** `grep -r "datetime\.\(utcnow\|now\)" src/components/`
- [ ] **Quality gate:** Fail build if datetime.utcnow/now found in components
- [ ] **Tests use fake time:** Inject deterministic time adapter in tests

---

### Lesson: Global state in components violates determinism - use StoragePort

**What happened:**

The auth component used a module-level dict for session storage:
```python
# BAD - global state
_SESSIONS: dict[str, Session] = {}

def run_create_session(...):
    _SESSIONS[token] = session  # Side effect on global state
```

**Problems:**
- State persists across test runs (test isolation broken)
- Can't scale to multiple processes
- Violates deterministic core principle
- Makes testing require module-level patching

**The fix:**

```python
# ports.py
class SessionStorePort(Protocol):
    def get(self, token: str) -> Session | None: ...
    def save(self, token: str, session: Session) -> None: ...
    def delete(self, token: str) -> None: ...

# adapters/auth/session_store.py
class InMemorySessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}  # Instance state, not global
    ...

# component.py
def run_create_session(
    inp: CreateSessionInput,
    session_store: SessionStorePort,  # Injected
) -> AuthOutput:
    session_store.save(token, session)  # No global state
```

### Future Checklist:
- [ ] **Grep for global state:** `grep -r "^[A-Z_]*: dict\[" src/components/`
- [ ] **Any mutable module-level variable is a violation**
- [ ] **Create Port protocol for any storage need**
- [ ] **Inject adapter via dependency injection**

---

## 14. _impl.py Re-export Pattern

### Lesson: Never import from _impl.py directly - re-export through __init__.py

**What happened (QA Audit 2026-01-12):**

14 files imported directly from `_impl.py`:
```python
# BAD
from src.components.audit._impl import AuditService

# GOOD
from src.components.audit import AuditService
```

**Why direct imports are problematic:**
- Couples external code to internal structure
- Can't refactor `_impl.py` without breaking imports
- Bypasses the component's public API
- Makes deprecation difficult

**The fix:**

```python
# src/components/audit/__init__.py

# Re-exports from _impl for backwards compatibility
from ._impl import (
    AuditService,
    InMemoryAuditRepo,
)

__all__ = [
    ...
    "AuditService",
    "InMemoryAuditRepo",
]
```

### Future Checklist:
- [ ] **Quality gate:** `grep -r "from src\.components\.\w+\._impl" src/` returns empty
- [ ] **All _impl exports go through __init__.py**
- [ ] **External code uses:** `from src.components.X import Y`
- [ ] **Sunset plan:** Eventually move _impl.py code into component.py

---

### Lesson: Type conflicts between _impl.py and models.py require careful ordering

**What happened:**

Both `models.py` and `_impl.py` defined `AuditAction`:
- `models.py`: `AuditAction = Literal["create", "update", ...]`
- `_impl.py`: `class AuditAction(str, Enum): ...`

When ruff sorted imports alphabetically, `_impl` came first, then `models` redefined `AuditAction`, causing:
- `TypeError: Cannot instantiate typing.Literal`
- Type mismatches between what API routes expected vs what services returned

**The fix:**

1. Import from `_impl.py` first (in __init__.py)
2. Remove duplicate names from `models.py` import
3. The `_impl.py` version "wins" and provides correct types

```python
# CORRECT ordering in __init__.py
from ._impl import (
    AuditAction,    # Enum version - this one is used
    AuditEntry,
    EntityType,
)
from .models import (
    # AuditAction removed - would conflict
    # AuditEntry removed - would conflict
    AuditEntryOutput,
    AuditListOutput,
    ...
)
```

### Future Checklist:
- [ ] **Before re-exporting:** Check for duplicate class names in _impl.py and models.py
- [ ] **Choose one source:** Usually _impl.py for Enum classes, models.py for dataclasses
- [ ] **Remove duplicates:** Don't import same name from both files
- [ ] **Run mypy:** Type conflicts surface as "incompatible type" errors

---

## 15. Next.js & TipTap Rich Text Integration

### Lesson: TipTap requires separate packages for editing vs rendering

**What happened (EV-0003, 2026-01-13):**

The TipTap editor worked fine for editing content, but published articles showed "Error rendering content". The issue: `generateHTML()` requires `@tiptap/html` package, which wasn't installed.

**The fix:**
```bash
npm install @tiptap/html
```

```typescript
// block-renderer.tsx
import { generateHTML } from "@tiptap/html";  // NOT @tiptap/core
import StarterKit from "@tiptap/starter-kit";

const extensions = [StarterKit, Link, Image];
const html = generateHTML(tiptapJson, extensions);
```

### Future Checklist:
- [ ] Install `@tiptap/html` for server-side/static HTML generation
- [ ] Use same extensions array for editor and renderer
- [ ] Test rendering separately from editing

---

### Lesson: Radix Toggle components can be unreliable with controlled state

**What happened:**

Toolbar buttons using Radix UI `<Toggle>` with controlled `pressed` prop weren't responding to clicks. The `onPressedChange` callback fired but the UI didn't update.

**Root cause:** Complex interaction between controlled `pressed` prop derived from `editor.isActive()` and the Toggle's internal state management.

**The fix:** Replace Toggle with standard Button:

```typescript
// BAD - Toggle with controlled state can be flaky
<Toggle
  pressed={editor.isActive("bold")}
  onPressedChange={() => editor.chain().focus().toggleBold().run()}
>

// GOOD - Button with onClick is reliable
<Button
  type="button"
  variant="ghost"
  className={cn(editor.isActive("bold") && "bg-accent")}
  onClick={() => editor.chain().focus().toggleBold().run()}
>
```

### Future Checklist:
- [ ] Prefer Button over Toggle for toolbar actions
- [ ] Always add `type="button"` to prevent form submission
- [ ] Use className for active state styling instead of controlled prop

---

## 16. Next.js Static vs Dynamic Rendering

### Lesson: Content pages need dynamic rendering to avoid stale data

**What happened:**

User deleted content but it still appeared on homepage. The page was statically generated at build time and cached.

**The fix:**
```typescript
// app/page.tsx
export const dynamic = 'force-dynamic';  // Force server-render on each request
```

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| Static (default) | Fast, cached at edge | Stale until rebuild |
| `force-dynamic` | Always fresh | Slower, no edge caching |
| `revalidate: 60` | Periodic refresh | Up to 60s stale |

### Future Checklist:
- [ ] Content listing pages should use `force-dynamic` or `revalidate`
- [ ] Static pages are fine for truly static content (about, docs)
- [ ] Check build output: `○` = static, `ƒ` = dynamic

---

## 17. Tailwind CSS v4 Plugin Configuration

### Lesson: Tailwind v4 uses @plugin directive, not @import for plugins

**What happened:**

Build failed with "Can't resolve '@tailwindcss/typography'" when using:
```css
@import "@tailwindcss/typography";  /* WRONG in v4 */
```

**The fix:**
```css
@import "tailwindcss";
@import "tw-animate-css";
@plugin "@tailwindcss/typography";  /* CORRECT in v4 */
```

### Future Checklist:
- [ ] In Tailwind v4, use `@plugin` for official plugins
- [ ] Third-party CSS can still use `@import`
- [ ] Check Tailwind v4 migration guide for syntax changes

---

## 18. Frontend-Backend Data Format Alignment

### Lesson: Create explicit transformation layers when frontend and backend schemas differ

**What happened:**

Frontend editor used `body` (TipTap JSON), backend expected `blocks` array with `data_json.tiptap`. Content saved but didn't display because formats were incompatible.

**The fix - transformation layer in ContentService:**

```typescript
// Convert TipTap JSON to backend blocks format
function bodyToBlocks(body: any): BackendBlock[] {
    if (!body || Object.keys(body).length === 0) return [];
    return [{
        block_type: "markdown",
        data_json: { tiptap: body }
    }];
}

// Convert backend blocks to TipTap JSON
function blocksToBody(blocks: BackendBlock[]): any {
    const first = blocks[0];
    if (first?.data_json?.tiptap) return first.data_json.tiptap;
    return {};
}

// Transform responses
function transformResponse(data: any): ContentItem {
    return {
        ...data,
        body: blocksToBody(data.blocks || []),
        description: data.summary || "",
    };
}
```

### Future Checklist:
- [ ] Document frontend vs backend schemas explicitly
- [ ] Create transformation functions at API client layer
- [ ] Transform on every request/response, not in components
- [ ] Test round-trip: create → save → fetch → display

---

## 55. Claude Code Slash Command Syntax Limitations

### Lesson: Avoid $() command substitution inside !` ` dynamic execution in slash commands

**What happened (claude-architecture-diagrams, 2026-01-31):**

The custom `/learn` slash command failed with error:
```
Error: Bash command permission check failed for pattern "!`basename $(pwd)`":
Command contains $() command substitution
```

The command template used nested command substitution which isn't supported:
```markdown
- Current project: !`basename $(pwd)`   ← $() not allowed inside !` `
```

Claude Code's `!` backtick syntax for dynamic command execution doesn't support nested `$()` command substitution within the backticks.

**The fix:**

Replace complex commands with simpler alternatives that avoid `$()`:

```markdown
# BEFORE (broken)
- Current project: !`basename $(pwd)`

# AFTER (works)
- Current directory: !`pwd`
```

Alternative approaches if you need the basename:
```bash
# Use pipes instead of $()
pwd | xargs basename

# Or just use full path and let Claude extract project name
pwd
```

### Future Checklist:
- [ ] Avoid `$()` command substitution inside `!` backticks in slash command templates
- [ ] Test slash commands after creating/modifying them
- [ ] Use simple commands in `!` backticks - prefer pipes over nested substitution
- [ ] When command fails with "permission check failed", check for `$()` in the pattern

---

### Lesson 57: Unifying Multi-Location Agent Configurations into a Single Installable Repository

**What happened (claude-agent-framework, 2026-02-03):**

Over time, an organically-grown Claude agent ecosystem became spread across three locations: `~/.claude/` (agents, docs, schemas), `~/Developer/claude/prompts/` (system prompts, playbooks, devlessons.md), and `~/.dotfiles/claude/.claude/` (CLAUDE.md, settings). This fragmentation made it impossible to version the system as a whole, share it via GitHub, or roll back to a previous known-good state. Updating one component required knowing which of three directories to modify.

**The fix:**

Consolidate everything into a single git repository with symlink-based installation:

```
claude-agent-framework/
├── agents/           # Agent prompt definitions
├── prompts/
│   ├── system/       # System prompts (methodology)
│   └── playbooks/    # Practical guides
├── schemas/          # Validation schemas
├── docs/             # Governance documentation
├── lenses/           # Persona lens packs
├── patterns/         # CI/CD and architecture patterns
├── scripts/
│   ├── install.sh    # Creates symlinks to ~/.claude/
│   ├── snapshot.sh   # Creates timestamped backup
│   └── rollback.sh   # Restores from snapshot
├── knowledge/
│   └── devlessons.md # Accumulated lessons
├── config/           # Templates for local config
├── versions/         # Bi-temporal version tracking
├── manifest.yaml     # Component versions and dependencies
└── CLAUDE.md         # Global instructions
```

The installer creates symlinks from `~/.claude/` to the repo, keeping a single source of truth:

```bash
# Content is symlinked (version controlled)
~/.claude/agents -> ~/Developer/claude-agent-framework/agents/

# State stays local (not tracked)
~/.claude/devops/manifest.yaml  # Your portfolio state
~/.claude/settings.local.json   # Machine-specific config
```

**Key design decisions:**
1. **Symlinks for content** - Changes to repo apply immediately via `git pull`
2. **Local state preserved** - devops state, settings, history not tracked in repo
3. **Config templates** - Repo has `.template` files; installer copies to local if missing
4. **Backup on install** - Previous state saved to `~/.claude-backup-YYYYMMDD-HHMMSS/`

### Future Checklist:
- [ ] Separate content (shareable) from state (instance-specific) from config (machine-specific)
- [ ] Use symlinks for single source of truth - enables instant updates via git pull
- [ ] Include install.sh that creates symlinks and backup, uninstall.sh that removes them
- [ ] Create snapshot/rollback scripts for version management before symlinking
- [ ] Keep manifest.yaml with component versions and dependency graph
- [ ] Template config files (`.template`) that get copied on first install, never overwritten
- [ ] Update all hardcoded paths in CLAUDE.md to use `~/.claude/` symlink paths

---

### Lesson 118: Agent CLI Tools Architecture - Scripts vs Packages

**What happened (claude-agent-framework, 2026-02-04):**

When building a multi-agent framework with various CLI tools (validation scripts, deployment helpers, database utilities), the question arose: where should these tools live? Initially, tools were scattered or there was uncertainty about whether to include everything in the framework repo or create separate packages.

The solution was a two-tier approach: **framework scripts** for simple, framework-specific utilities stay in `scripts/` folder, while **external packages** with their own dependencies and broader reusability become separate repositories. A central `tools/registry.yaml` manifest tracks all tools regardless of location.

**The decision criteria:**

| Criteria | Script (in framework) | Separate Repo |
|----------|----------------------|---------------|
| Lines of code | < 500 | > 500 |
| Dependencies | Minimal (stdlib only) | Has own deps |
| Reuse outside framework | No | Yes |
| Versioning needs | Follow framework | Independent |
| Testing requirements | Simple | Comprehensive |

**The registry pattern:**

```yaml
# tools/registry.yaml
schema_version: "1.0"

scripts:
  validate_agents:
    path: "scripts/validate_agents.py"
    description: "Validate agent prompts against schema"
    used_by: [ops, qa]

packages:
  db-harness:
    repository: "https://github.com/org/db-harness"
    version: "1.0.0"
    install: "pip install git+https://github.com/org/db-harness.git@v1.0.0"
    used_by: [ops]
    gates_implemented: [NN-DB-1, NN-DB-2, NN-DB-3, NN-DB-4]
```

### Future Checklist:
- [ ] Keep simple framework-specific scripts (<500 LOC, stdlib) in `scripts/` folder
- [ ] Create separate repos for tools with dependencies or broader reusability (>500 LOC)
- [ ] Maintain `tools/registry.yaml` as central manifest of all tools (scripts + packages)
- [ ] Include `used_by` field to track which agents depend on each tool
- [ ] Include `decision_ref` to link tools to decision records
- [ ] For packages: specify version, install command, and gates/features implemented

---

## Summary: Top 30 Rules for Future Projects

1. **Choose mature frameworks** - community size and API stability matter more than "cool"
2. **Pin all dependencies** - especially transitive ones that can break your stack
3. **Use clean architecture** - ports/adapters enables painless pivots
4. **Run quality gates constantly** - after every task, not just at release
5. **Create BA artifacts first** - spec, tasklist, rules before coding
6. **Track drift explicitly** - evolution.md catches scope creep
7. **Different layers need different tests** - don't force TDD on UI
8. **Fly.io needs volumes** - create before deploy, size appropriately
9. **Document deployment quirks** - PYTHONPATH, health checks, cold starts
10. **One task at a time** - prevents chaos and enables handoffs
11. **Read the playbook BEFORE coding** - familiar patterns cause silent drift (36%→95% compliance fix)
12. **Contracts first, code second** - contract.md is the spec, not documentation
13. **Audit early and often** - compliance checks must run with every quality gate
14. **TDD on contracts, not just code** - test the component spec to prevent scope drift
15. **Find ALL components before migration** - audit entire codebase, not just obvious directories
16. **External QA validates migrations** - split-brain states hide from internal review
17. **Manifest + Tasklist paths = Definition of Done** - stale paths mean task not complete
18. **Deprecate with sunset dates** - "eventually remove" becomes permanent debt
19. **Use deprecation warnings** - silent migrations let old code linger
20. **Complete ALL layers in migrations** - never leave split implementations across domain and shell
21. **Use DEPRECATED.md with explicit migration maps** - developers need to know old → new locations
22. **Add migration-specific quality gates** - verify zero old imports, not just passing tests
23. **Inject TimePort for all time operations** - `datetime.utcnow()` in components violates determinism
24. **No global state in components** - use injected StoragePort instead of module-level dicts
25. **Re-export _impl.py through __init__.py** - external code should never import from _impl directly
26. **Resolve type conflicts when re-exporting** - remove duplicates when _impl.py and models.py define same names
27. **Install @tiptap/html for rendering** - editor package doesn't include server-side HTML generation
28. **Use Button over Toggle for toolbars** - Radix Toggle with controlled state can be unreliable
29. **Content pages need force-dynamic** - Next.js static caching shows stale data until rebuild
30. **Create API transformation layers** - when frontend/backend schemas differ, transform at service layer

---

## References

- EV-0001: Atomic Component Remediation (Domain Layer)
- EV-0002: Shell Layer Migration (API/Routes layer)
- EV-0003: Continuous Type Safety
- EV-0004: Frontend Migration (Flet→React)
- D-0001 through D-0005: Architectural decisions
- `research-lab-bio_evolution.md`: Full drift history
- `research-lab-bio_decisions.md`: Full decision log

### Atomic Component Remediation (2026-01-12)
- `little-research-lab/RETROSPECTIVE_2026-01-12.md`: Full remediation retrospective
- `little-research-lab/REMEDIATION_PLAN.md`: 3-phase remediation plan
- `little-research-lab/little-research-lab-v3_evolution.md` (EV-0001): Architectural drift entry
- `universal_coding_agent_playbook.md`: Section 2 (Component Structure) - the standard that was violated

### Follow-Up Assessment & Full Alignment (2026-01-12)
- External QA assessment identified split-brain state (5 components in wrong location)
- `little-research-lab/src/services/DEPRECATED.md`: Legacy deprecation notice
- Parallel agent execution created 5 components in ~20 seconds
- Manifest updated: C0-C13 (14 components total)
- Tasklist synchronized: 15 path references updated

### Shell Layer Migration (2026-01-12, EV-0002)
- 36 shell layer files migrated from `src.core.services` to `src.components.*._impl`
- 61 mypy errors resolved through complete type coverage
- 58 ruff lint violations fixed
- 4-phase migration: DEPRECATED.md → _impl.py → Import updates → Quality gates
- `src/core/services/DEPRECATED.md`: Migration map with sunset date
- `little-research-lab-v3_evolution.md` (EV-0002): Full resolution notes

### QA Audit & Determinism Remediation (2026-01-12)

**Session Statistics:**
| Metric | Value |
|--------|-------|
| Architectural violation types | 4 |
| Components with time I/O fixed | 4 |
| datetime.utcnow/now calls removed | 13 |
| Global state violations fixed | 1 |
| _impl.py re-exports added | 8 |
| External imports updated | 14 |
| Type conflicts resolved | 3 |
| Test files updated (rules path) | 31 |
| Total tests passing | 1253 |

**Files Modified:**
- Component __init__.py (re-exports): 8
- Component ports.py (new ports): 4
- Component component.py (DI updates): 4
- API routes (import updates): 9
- Shell hooks (import updates): 1
- Adapters created: 1 (InMemorySessionStore)

**Knowledge Base Updates:**
- devlessons.md: +2 sections, +4 rules (22→26)
- RESTART_PROMPT.md: Complete rewrite with session context

**Evidence:** `little-research-lab/RESTART_PROMPT.md`

### Playwright E2E Testing & Final Integration (2026-01-12)

**Commit Statistics:**
| Commit | Description | Files | Insertions | Deletions |
|--------|-------------|-------|------------|-----------|
| `d634cd1` | Fix QA review issues: redirects, domain entity, test fixtures | 5 | +382 | -169 |
| `a610654` | Add Playwright E2E test suite with data-testid attributes | 33 | +1,927 | -19 |
| `73f2cf5` | Add admin pages, editor components, scheduler improvements | 29 | +2,470 | -437 |
| **Total** | | **67** | **+4,779** | **-625** |

**Test Results:**
| Suite | Result |
|-------|--------|
| Playwright E2E | 9/9 passing |
| Unit tests | 1183/1183 passing |

**QA Compliance:**
| Metric | Before | After |
|--------|--------|-------|
| Overall compliance | 46.5% | ~95% |
| Critical issues | 14 | 0 |

**Issues Resolved:**
| Type | Count |
|------|-------|
| Duplicate function definitions | 1 |
| Missing domain entities | 1 |
| Protocol compliance fixes | 1 |
| Test DI pattern rewrites | 2 |
| Playwright test fixes | 3 |
| Data-testid additions | 6 |
| Next.js middleware errors | 1 |

**Files Modified by Category:**
| Category | Count |
|----------|-------|
| Frontend components | 18 |
| Frontend pages | 8 |
| Backend API routes | 4 |
| Domain/adapters | 3 |
| Tests | 6 |
| Config/misc | 5 |

**Lessons Documented:** 7 new lessons covering:
- Dialog-based UI testing with Playwright
- Playwright strict mode handling
- Next.js middleware caching issues
- Python protocol compliance
- Type hint shadowing with built-ins
- Test parallelism and race conditions
- Domain layer entity organization

**Evidence:** Git commits `d634cd1`, `a610654`, `73f2cf5` pushed to `origin/main`

### Frontend Integration & Rich Text Fixes (2026-01-13, EV-0003)

**Session Statistics:**
| Metric | Value |
|--------|-------|
| Issues identified | 5 |
| Packages installed | 2 (@tiptap/html, @tailwindcss/typography) |
| Components refactored | 2 (Toolbar.tsx, block-renderer.tsx) |
| Services updated | 1 (ContentService.ts) |
| Pages fixed | 1 (app/page.tsx) |
| CSS files updated | 1 (globals.css) |
| Commits | 6 |
| Deployments to fly.io | 5 |

**Issues Resolved:**
| Issue | Root Cause | Fix |
|-------|------------|-----|
| Article content not rendering | Missing @tiptap/html package | npm install @tiptap/html |
| Toolbar buttons not working | Radix Toggle controlled state issue | Replace with Button components |
| Deleted content still showing | Next.js static page caching | export const dynamic = 'force-dynamic' |
| Missing paragraph spacing | No typography plugin | @plugin "@tailwindcss/typography" |
| Content format mismatch | body vs blocks schema difference | Add transformation layer |

**Files Modified:**
| File | Change |
|------|--------|
| frontend/components/editor/Toolbar.tsx | Toggle → Button |
| frontend/components/content/block-renderer.tsx | Add generateHTML |
| frontend/lib/api/services/ContentService.ts | Add body↔blocks transforms |
| frontend/app/page.tsx | Add force-dynamic |
| frontend/app/globals.css | Add @plugin typography |
| frontend/package.json | Add dependencies |

**Lessons Documented:** 4 new lessons covering:
- TipTap editing vs rendering packages
- Radix Toggle reliability issues
- Next.js static vs dynamic rendering
- Frontend-backend schema transformation

**Evidence:** Commits 5e0d426→31c1d53 pushed to `origin/main`, EV-0003 in evolution.md

### ESLint Error Remediation (2026-01-13)

**Session Statistics:**
| Metric | Value |
|--------|-------|
| Errors fixed | 13 |
| Files modified | 8 |
| New interfaces added | 7 |
| Warnings remaining | 27 (non-blocking) |

**Patterns Applied:**

1. **API Error Typing:**
```typescript
// Define error shape for API responses
interface ApiError {
    body?: { detail?: string; errors?: ValidationError[] };
}

// Use type assertion instead of any
catch (error) {
    const err = error as ApiError;
    toast.error(err.body?.detail || "Failed");
}
```

2. **Collection Item Typing:**
```typescript
// Define types for API response items
interface PublicPost {
    id: string;
    title: string;
    slug: string;
}

// Use in map instead of any
posts.map((post: PublicPost) => ...)
```

3. **React Purity Violations:**
```typescript
// BAD - Math.random() during render
const width = React.useMemo(() => {
    return `${Math.floor(Math.random() * 40) + 50}%`
}, [])

// GOOD - Use fixed value
const width = "70%"
```

4. **ESLint Disable Comments:**
```typescript
// When type cast is unavoidable (e.g., zodResolver)
// eslint-disable-next-line @typescript-eslint/no-explicit-any
resolver: zodResolver(formSchema) as any,
```

**Evidence:** Commit 4090696 pushed to `origin/main`

---

## 15. Python Keyword as Module Name

### Lesson: Avoid Python keywords as module/folder names in atomic components

**What happened:**
In the atomic component pattern, we use `fc/` for Functional Core and `is/` for Imperative Shell. However, `is` is a Python keyword, causing import syntax errors:

```python
# This fails - 'is' is a keyword
from src.components.C2_PublicTemplates.is import RevalidationAdapter
# SyntaxError: invalid syntax
```

**Resolution:**
Use `importlib` to dynamically import from keyword-named modules and re-export through the parent `__init__.py`:

```python
# In component's __init__.py
import importlib

# Import IS module (named 'is' which is a Python keyword)
_is_module = importlib.import_module("src.components.C2_PublicTemplates.is")
RevalidationAdapter = _is_module.RevalidationAdapter
RevalidationResult = _is_module.RevalidationResult
StubRevalidationAdapter = _is_module.StubRevalidationAdapter

__all__ = [
    # ... FC exports ...
    "RevalidationAdapter",
    "RevalidationResult",
    "StubRevalidationAdapter",
]
```

Then consumers import from the main module:
```python
# Clean import from main module
from src.components.C2_PublicTemplates import RevalidationAdapter, StubRevalidationAdapter
```

### Future Checklist:
- [ ] Use `shell/` or `imperative/` instead of `is/` for Python atomic components
- [ ] If `is/` is mandated by convention, always re-export through parent `__init__.py`
- [ ] Test imports in isolation before writing dependent code

**Evidence:** T-0011 implementation, test_caching_policy.py import fix

---

## 16. Sitemap Filtering Semantics

### Lesson: Content without publication date should be excluded from sitemaps

**What happened:**
The `filter_sitemap_entries` function processed entries as (slug, content_type, published_at, updated_at) tuples and passed them to `should_include_in_sitemap("published", published_at, now)`. When `published_at` was `None`, the function incorrectly included the entry because:
1. State was hardcoded as "published"
2. `should_include_in_sitemap` only excluded future-dated content, not missing dates

```python
# Bug: entries with published_at=None were included
entries = [
    ("post-1", "post", past_time, past_time),  # ✓ Included correctly
    ("draft-1", "post", None, None),           # ✗ Incorrectly included
]
```

**Resolution:**
Add explicit check for `None` published_at before other filtering:

```python
for slug, content_type, published_at, updated_at in entries:
    # No published_at means content isn't published - exclude
    if published_at is None:
        continue
    # Only include published content that's not future-dated
    if not should_include_in_sitemap("published", published_at, now):
        continue
```

### Future Checklist:
- [ ] When filtering by publication status, always handle `None` dates explicitly
- [ ] Document semantic meaning: `published_at=None` means "not yet published"
- [ ] Write tests for edge cases (None dates, future dates, past dates)
- [ ] R2 invariant (draft isolation) applies to sitemap generation

**Evidence:** T-0011 test failure fix, test_filter_sitemap_entries_excludes_drafts

---

## 17. Cache Header Configuration Location

### Lesson: Consider rules.yaml vs hardcoded constants trade-off

**What happened:**
Cache header values were implemented as module-level constants in FC:

```python
DEFAULT_PUBLISHED_CACHE_CONTROL = (
    "public, max-age=0, s-maxage=300, stale-while-revalidate=86400"
)
DEFAULT_PRIVATE_CACHE_CONTROL = "private, no-store"
DEFAULT_IMMUTABLE_CACHE_CONTROL = "public, max-age=31536000, immutable"
```

QA review noted these could be moved to `rules.yaml` for rules-first execution compliance.

**Trade-off Analysis:**

| Approach | Pros | Cons |
|----------|------|------|
| Hardcoded constants | Simple, no I/O in FC, fast | Requires code change to modify |
| Rules.yaml injection | Runtime configurable, rules-first | Added complexity, parameter passing |

**Decision:** Accepted as-is for T-0011. Cache headers rarely change and are tied to infrastructure (CDN configuration). The values are well-documented in code.

### Future Checklist:
- [ ] For policies that change frequently → put in rules.yaml
- [ ] For infrastructure-tied values that rarely change → constants acceptable
- [ ] Always document the source of values in comments
- [ ] If extracting to rules.yaml later, create follow-up task

---

## 18. Radix UI Select Empty Value Constraint

### Lesson: Radix UI Select does not allow empty string values for SelectItem

**What happened:**
During Playwright UI testing of the resources admin page, the page crashed with error:
```
A <Select.Item /> must have a value prop that is not an empty string.
This is because the Select value can be set to an empty string to clear
the selection and show the placeholder.
```

**Root cause:**
Radix UI's Select component (used by shadcn/ui) reserves empty string `""` for its internal "no selection" state. Using `<SelectItem value="">` conflicts with this.

**Original code (crashes):**
```tsx
const [pdfAssetId, setPdfAssetId] = useState<string>("")

<Select value={pdfAssetId} onValueChange={setPdfAssetId}>
  <SelectItem value="">No PDF selected</SelectItem>  // ❌ Empty string crashes
  {assets.map(a => <SelectItem key={a.id} value={a.id}>{a.name}</SelectItem>)}
</Select>
```

**Fixed code (works):**
```tsx
const [pdfAssetId, setPdfAssetId] = useState<string>("")

<Select
  value={pdfAssetId || "__none__"}  // Transform "" to sentinel for display
  onValueChange={(v) => setPdfAssetId(v === "__none__" ? "" : v)}  // Transform back
>
  <SelectItem value="__none__">No PDF selected</SelectItem>  // ✅ Non-empty sentinel
  {assets.map(a => <SelectItem key={a.id} value={a.id}>{a.name}</SelectItem>)}
</Select>
```

**Pattern explanation:**
- Use sentinel value `"__none__"` (or `"_none"`, `"NONE"`) for the "no selection" option
- Transform state at the Select boundary: display uses sentinel, internal state uses `""`
- This is the adapter pattern at the UI component level

### Future Checklist:
- [ ] When using shadcn/ui Select for optional fields, never use `value=""`
- [ ] Use a sentinel value pattern: `"__none__"` → `""` transformation
- [ ] Consider extracting to a reusable hook if pattern appears 3+ times:
  ```tsx
  const { selectValue, onSelectChange } = useOptionalSelect(state, setState)
  ```
- [ ] Document this constraint in your project's design system notes
- [ ] Test Select components with Playwright to catch similar issues early

**Evidence:** EV-0004, T-0020 related; discovered via Playwright MCP testing 2026-01-14

## 18. Component Export Alignment & Legacy Service Migration

### Session: 2026-01-14 - Component Export Alignment

This session focused on resolving subtle issues that occur when migrating from legacy service-based architectures to atomic component patterns. The core problem: inconsistency between what gets exported from `_impl.py` files versus what legacy factories create, causing type mismatches at runtime.

---

### Lesson: Component Export Consistency - Ensure factory functions create instances of the exported class

**What happened:** A component's `__init__.py` re-exported classes from `_impl.py`, but legacy factory functions were creating instances of a different class.

**Problem:** When tests checked `isinstance(service, ExportedService)`, the factory's instance failed because it was actually from a different class.

**The fix:** The factory function must return instances of the same class that's exported from `__init__.py`. Don't have duplicate classes with similar names.

**Future Checklist:**
- [ ] When creating `_impl.py`, have ONE service class (not separate `...Impl` variant)
- [ ] All factories in `_impl.py` should return instances of that same class
- [ ] `__init__.py` re-exports exactly what's defined in `_impl.py`
- [ ] Test `isinstance(factory_result, ExportedClass)` to verify alignment

---

### Lesson: Enum vs Literal Type Conflicts - Python Enum and Literal types are not interchangeable

**What happened:** A component defined a type as both `Literal['bot', 'real']` in models.py and `class UAClass(str, Enum)` in _impl.py. Import order caused shadowing.

**The fix:** Choose ONE representation - usually the Enum is more useful at runtime. Remove the Literal from models.py and import only from _impl.py.

**Future Checklist:**
- [ ] Don't define the same name as both Literal and Enum
- [ ] If you have both, remove the Literal from models.py
- [ ] Test uses enum members: `assert result == UAClass.REAL` (not string comparison)

---

### Lesson: Function Signature Variants - Different signatures with same function name will break tests

**What happened:** `build_canonical_url(base_url, path)` vs `build_canonical_url(path, base_url=None, config=None)` - tests written for old signature failed with new one.

**The fix:** Don't try to unify incompatible signatures. Export both with distinct names:
- `build_canonical_url` - legacy signature for backward compatibility
- `build_canonical_url_with_config` - new API with config support

**Future Checklist:**
- [ ] When moving functions between modules, preserve the original signature
- [ ] If new requirements need different parameters, create a new function name
- [ ] Document why the old variant still exists

---

### Lesson: Exception Class Identity - Exception catching checks class identity, not name

**What happened:** Legacy functions raised `RulesValidationError` from the legacy module, but the component defined its own `RulesValidationError`. `pytest.raises()` checks class identity.

**The fix:** Always import and re-export the SAME exception class from the legacy module. Don't define duplicate exception classes.

**Future Checklist:**
- [ ] Grep for duplicate exception class definitions
- [ ] Import exception classes from their original location
- [ ] Re-export through `__init__.py`

---

### Lesson: ESLint React Compiler Rule - setState in useEffect triggers cascading renders warning

**What happened:** `setMounted(true)` called synchronously inside useEffect triggered a React compiler error about cascading renders.

**The fix:** Wrap state updates in `requestAnimationFrame` with proper cleanup:

```typescript
useEffect(() => {
    const frameId = requestAnimationFrame(() => {
        setMounted(true);
    });
    return () => cancelAnimationFrame(frameId);
}, []);
```

---

### Lesson: Ruff Auto-Fix Import Order - Run ruff after manual __init__.py edits

**What happened:** Manual edits to `__init__.py` added imports, but running `ruff check --fix` normalized the import format and order.

**The lesson:** After manually editing `__init__.py` to add re-exports, immediately run `ruff check --fix` to let it normalize the imports.

---

### Lesson: Migration Pattern for _impl Files - Each component should be self-contained

**What happened:** Mixing legacy factory functions with _impl service classes caused type inconsistencies.

**The fix:** Each component defines its own service class AND factory in `_impl.py`. Don't import legacy factories - create new ones that return the component's own classes.

**Key principle:** The `_impl.py` file is self-contained. Factory creates instances of the class defined in the same file.

---

### Remediation Session Statistics (2026-01-14)

| Metric | Value |
|--------|-------|
| Components fixed | 6 (analytics, render, settings, audit, redirects, rules) |
| Test failures resolved | 12 → 0 |
| Export consistency issues | 3 fixed |
| Enum/Literal conflicts | 2 resolved |
| Function signature variants | 1 created |
| React compiler fixes | 1 |

**Key Takeaway:** Legacy-to-component migrations have subtle pitfalls related to type identity and class consistency. Always ensure what gets exported matches what factories actually return.

---

## 19. MCP Server & FastMCP Architecture Patterns

**Project**: Bureaucrat MCP v1.0
**Date**: 2026-01-16
**Evidence**: `/Users/naidooone/Documents/thatcher/`

Built a complete Model Context Protocol (MCP) server with 9 atomic components, 31 tasks, 326 tests, and 4 resolved architectural decisions. This project demonstrated enterprise patterns for serverless agent coordination.

### Project Statistics

| Metric | Value |
|--------|-------|
| Tasks completed | 31/31 (100%) |
| Tests passing | 326 (100% pass rate) |
| Test-to-code ratio | 1.06:1 |
| Source LOC | 5,123 |
| Test LOC | 5,438 |
| Atomic components | 9 |
| Evolution items resolved | 4 |
| Architectural decisions | 8 |
| Quality gates | All passing (ruff, mypy, pytest) |

---

### Lesson: MCP Tools Must Be Non-Blocking (<200ms Response Time)

**What happened:**
The MCP specification requires tool handlers to return quickly. Claude and other MCP clients expect responses in <200ms under normal conditions. If a tool handler blocks on API calls or file I/O, the client experiences timeout-like behavior.

**The pattern:**

```python
@app.tool()
def commission_job(topic: str, save_as: str) -> dict:
    """
    Commission a job WITHOUT waiting for execution.
    Returns immediately (<200ms) by spawning background thread.
    """
    # Validate inputs (milliseconds)
    if not re.match(rules.inputs.save_as.regex, save_as):
        raise JobValidationError(f"Invalid save_as: {save_as}")

    # Create job in registry (milliseconds)
    job = Job.create(job_id, topic, save_as, time=time_port)
    registry.add_job(job)

    # Spawn thread for background work (milliseconds)
    thread = threading.Thread(
        target=run_job,
        args=(job_id, registry, drafter, auditor),
        daemon=True
    )
    thread.start()

    # Return immediately - work happens in thread
    return {"job_id": job_id, "status": "PENDING"}
```

**Why this matters:**

| Mistake | Impact | Solution |
|---------|--------|----------|
| Blocking on API call in tool | Tool times out | Spawn thread, return immediately |
| Building artifact in handler | Slow response | Do I/O in thread |
| Synchronous loop over jobs | N API calls | Process each in separate thread |

### Future Checklist:
- [ ] MCP tools return in <200ms (measure with test)
- [ ] All blocking I/O happens in separate threads
- [ ] Use `threading.Thread(target=..., daemon=True)` for background work
- [ ] Provide `check_*` tool for polling job status

---

### Lesson: TimePort Pattern Enforces Determinism in Domain Models

**What happened (Critical Issue - EV-0004):**
QA audit found the Job domain model was calling `datetime.now()` directly, violating determinism:

```python
# WRONG - non-deterministic
class Job:
    @staticmethod
    def create(job_id: str, topic: str, save_as: str) -> 'Job':
        return Job(
            created_at=datetime.now(),  # Changes every call
            updated_at=datetime.now(),
        )
```

**The solution: TimePort interface with dependency injection**

```python
# core/domain/ports.py
class TimePort(Protocol):
    def now_utc(self) -> datetime: ...

# core/domain/job.py
class Job:
    @staticmethod
    def create(
        job_id: str, topic: str, save_as: str,
        time: TimePort,  # Injected dependency
    ) -> 'Job':
        now = time.now_utc()
        return Job(created_at=now, updated_at=now)

# Tests use fixed time
class FixedTimePort:
    def __init__(self, fixed: datetime):
        self._time = fixed
    def now_utc(self) -> datetime:
        return self._time

# Production uses real time
class SystemTimeAdapter:
    def now_utc(self) -> datetime:
        return datetime.now(timezone.utc)
```

### Future Checklist:
- [ ] Define `TimePort` protocol in domain/ports.py
- [ ] All domain methods requiring time accept `now: datetime` parameter
- [ ] Tests use `FixedTimePort` for determinism
- [ ] Quality gate: `grep -r "datetime.now" src/` returns empty

---

### Lesson: Each Thread Needs Its Own asyncio Event Loop

**What happened:**
Job execution happens in background threads. Each thread needs to run async code (Gemini API, OpenAI API), so it requires its own event loop.

**The pattern:**

```python
def run_job(job_id: str, ...) -> None:
    """Thread entrypoint - creates event loop for async work."""

    # WRONG - fails in background thread
    # loop = asyncio.get_event_loop()  # RuntimeError: no running loop

    # RIGHT - creates event loop for this thread
    result = asyncio.run(orchestrator.run(topic))  # Works
```

**Key insight:** `asyncio.run()` creates a new event loop, runs the coroutine, and cleans up. Use it once at thread entry point.

### Future Checklist:
- [ ] Each background thread calls `asyncio.run()` exactly once
- [ ] Never use `asyncio.get_event_loop()` in background thread
- [ ] Async adapters use `async def` methods

---

### Lesson: Atomic File Writes Prevent Corruption

**The pattern:**

```python
def write_artifact(content: str, path: Path, artifact_dir: Path) -> None:
    """
    Write atomically: lock → temp → replace.
    Readers never see partial content.
    """
    # Security: path doesn't escape artifact_dir
    if not str(path.resolve()).startswith(str(artifact_dir.resolve())):
        raise PathTraversalError(f"Path escapes artifact_dir")

    lock_path = Path(str(path) + ".lock")
    with FileLock(str(lock_path), timeout=30):
        tmp_path = Path(str(path) + ".tmp")
        try:
            tmp_path.write_text(content, encoding="utf-8")
            os.replace(tmp_path, path)  # ATOMIC on POSIX
        finally:
            tmp_path.unlink(missing_ok=True)
```

### Future Checklist:
- [ ] Use `tmp` → `os.replace` pattern for critical writes
- [ ] Use `FileLock` for concurrent safety
- [ ] Verify path stays under artifact directory
- [ ] Test concurrent writers don't corrupt

---

### Lesson: Rules Files Enable Fail-Fast Startup

**What happened:**
All configuration comes from `rules.yaml`. Server validates on startup and exits if invalid:

```yaml
inputs:
  save_as:
    max_len: 100
    regex: "^[a-z0-9][a-z0-9_-]*[a-z0-9]$"

jobs:
  timeout_seconds: 120

governance:
  audit_fail_blocks_completion: false
```

**Validation:**
```python
def load_rules() -> RulesConfig:
    if not rules_path.exists():
        raise RulesLoadError(f"Rules file not found")

    config = RulesConfig(**yaml.safe_load(rules_path.read_text()))
    re.compile(config.inputs.save_as.regex)  # Validate regex
    return config
```

### Future Checklist:
- [ ] Rules validated completely at startup
- [ ] Exit with non-zero if rules invalid
- [ ] Test startup with invalid rules

---

### Lesson: Document Execution Strategy When Ambiguous (D-0007)

**What happened:**
Spec said "asyncio.gather for parallel execution" but implementation was sequential (drafter → auditor). This was flagged as a violation in EV-0002.

**Resolution:** Spec revision, not code change. Sequential execution is correct because auditor needs draft context for meaningful audit.

```python
# Sequential: auditor sees draft output
draft_output = await drafter.draft(topic)
audit_output = await auditor.audit(topic, draft_output)  # Needs draft

# Parallel would be: auditor doesn't see draft (less useful)
draft, audit = await asyncio.gather(drafter.draft(topic), auditor.audit(topic, ""))
```

**Key lesson:** When implementation differs from spec, investigate WHY before "fixing". Sometimes the spec is wrong.

### Future Checklist:
- [ ] Document execution strategy in spec AND code comments
- [ ] If sequential vs parallel matters, add test asserting wall-clock time
- [ ] When spec conflicts with implementation, investigate before fixing

---

### Lesson: Component Manifest Validates Atomic Structure

**What happened:**
Created `component_manifest.json` documenting all 9 components and `check_manifest.py` to validate:

```bash
$ python scripts/check_manifest.py
Component Manifest Validation Report
==================================================
Components checked: 9
Total checks: 84
Passed: 84
Failed: 0
Result: ALL CHECKS PASSED
```

**Checks performed:**
- Directory exists
- Required files: component.py, models.py, ports.py, contract.md, __init__.py
- Exports match `__all__`
- Entry points exist
- Contract sections present

### Future Checklist:
- [ ] Create manifest.json documenting components
- [ ] Create check_manifest.py validator
- [ ] Run manifest check in quality gates
- [ ] Each component has contract.md

---

### Lesson: Telemetry Must Be Non-Fatal (NFR-RL1)

**What happened:**
Phoenix (OpenTelemetry collector) might be down. Telemetry failures must not fail jobs.

```python
class TelemetryManager:
    def span(self, name: str, **attributes):
        try:
            if not self._enabled:
                return NoOpSpan()
            return self._tracer.start_span(name, attributes=attributes)
        except Exception:
            return NoOpSpan()  # Never raise
```

### Future Checklist:
- [ ] Telemetry init catches all exceptions
- [ ] Span operations return NoOp on failure
- [ ] Test that jobs complete when telemetry disabled

---

### Key Architectural Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| D-0007 | Sequential execution | Auditor needs draft context |
| D-0008 | ARTIFACT_DIR configurable | With startup validation |
| TimePort | Inject timestamps | Deterministic testing |
| Non-blocking tools | Thread spawn | MCP <200ms requirement |
| Atomic writes | Lock+tmp+replace | No partial content visible |
| Rules-first | YAML config | Behavior changes without code |

---

### Evolution Items Resolved

| EV | Issue | Resolution |
|----|-------|-----------|
| EV-0001 | Multiple concerns | Split into EV-0002, EV-0003 |
| EV-0002 | Sequential vs parallel | Spec revision (D-0007) |
| EV-0003 | ARTIFACT_DIR safety | Startup validation (D-0008) |
| EV-0004 | Determinism violation | TimePort injection + atomic structure |

---

### Summary: Top 10 MCP & Async Patterns

1. **MCP tools return in <200ms** - spawn threads, check status later
2. **Rules validated at startup** - fail-fast with exit(1)
3. **Domain models inject time** - never datetime.now() directly
4. **Each thread needs asyncio.run()** - creates event loop
5. **Atomic writes: lock + tmp + replace** - no partial content
6. **Component contracts first** - contract.md before code
7. **Input validation from rules** - regex, lengths from YAML
8. **Telemetry is non-fatal** - Phoenix down doesn't fail jobs
9. **Manifest validates structure** - 84 automated checks
10. **State machines via protocols** - invalid transitions raise errors

---

## 20. Token Efficiency in MCP Tool Responses

**Date**: 2026-01-16
**Project**: Bureaucrat MCP Server v1

### Problem
MCP tools returning raw CLI output or verbose JSON waste context tokens. A docker build output can be 5,000+ tokens when only 50 are needed.

### Pattern
Return structured summaries with decision-critical fields first.

```python
# BAD - returns full log
return {"output": subprocess_result.stdout}  # 5000 tokens

# GOOD - structured summary
return {
    "status": "success",           # Decision field first
    "summary": "Built myapp:latest in 34s",
    "warnings": [],
    "details_available": True      # Offer follow-up if needed
}
```

### Checklist
- [ ] All MCP tools return status field first
- [ ] Verbose data offered via follow-up tool, not default
- [ ] Error responses include fix hints, not full stack traces

---

## 21. Provider Fallback Architecture

**Date**: 2026-01-16
**Project**: Bureaucrat MCP Server v1

### Problem
Cloud API quota exhaustion breaks workflows. Need graceful degradation to local models.

### Pattern
Fallback chain with error classification (recoverable vs fatal).

```python
validators = [("openai", openai_adapter), ("ollama", ollama_adapter)]

for provider, validator in validators:
    try:
        return validator.validate(code)
    except Exception as e:
        if is_quota_or_connection_error(e):
            continue  # Try next provider
        raise  # Fatal error, don't retry
```

### Evidence
Bureaucrat MCP QA validator - OpenAI → Ollama fallback on 429 errors.

### Checklist
- [ ] Define fallback chain in config, not hardcoded
- [ ] Classify errors: quota (429), connection, auth, other
- [ ] Log fallback events for monitoring

---

## 22. MCP Tool Response Time

**Date**: 2026-01-16
**Project**: Bureaucrat MCP Server v1

### Problem
MCP tools that block on slow operations (API calls, builds) create poor UX. Target: <200ms response time.

### Pattern
Spawn background work, return immediately with job ID.

```python
@mcp.tool()
def commission_job(topic: str) -> dict:
    job = registry.create_job(topic)  # Fast (~1ms)
    thread = threading.Thread(target=run_job, args=(job.id,), daemon=True)
    thread.start()
    return {"job_id": job.id, "status": "PENDING"}  # Returns in <10ms
```

### Checklist
- [ ] No API calls in MCP tool handlers
- [ ] Background threads for work >100ms
- [ ] Provide check_status tool for polling

---

## 23. Claude Desktop MCP Configuration

**Date**: 2026-01-16
**Project**: Bureaucrat MCP Server v1

### Problem
Claude Desktop doesn't expand ~ or resolve relative paths. Secrets in plaintext config are insecure.

### Pattern
Use absolute paths and shell wrappers for Keychain.

```json
{
  "mcpServers": {
    "myserver": {
      "command": "/bin/bash",
      "args": ["-c", "export API_KEY=$(security find-generic-password -a $USER -s MY_API_KEY -w) && /full/path/to/python -m myserver"],
      "env": {
        "CONFIG_PATH": "/Users/username/project/config.yaml"
      }
    }
  }
}
```

### Checklist
- [ ] All paths in Claude Desktop config are absolute
- [ ] Secrets fetched from Keychain at startup
- [ ] Test config by running command manually first

---

## 24. Atomic Component Pattern for MCP Adapters

**Date**: 2026-01-16
**Project**: Bureaucrat MCP Server v1

### Problem
External service integrations become tangled spaghetti without structure.

### Pattern
Each integration is an atomic component with standard files.

```
components/adapters/github/
├── component.py    # GitHubAdapter class + run_* entry points
├── models.py       # PRInput, PROutput, IssueInput, etc.
├── ports.py        # GitHubPort Protocol
├── contract.md     # API limits, error handling, auth
└── __init__.py     # Public exports
```

### Evidence
Bureaucrat MCP has 10 atomic components, all passing manifest validation.

### Checklist
- [ ] One adapter component per external service
- [ ] Stub adapter for testing (no real API calls)
- [ ] Contract documents rate limits and auth requirements

---

## 25. Solution Designer → BA → Coding Agent Workflow

**Date**: 2026-01-17
**Project**: Bureaucrat MCP Server v2

### Problem
Large feature sets need structured planning before implementation to avoid scope creep and ensure quality.

### Pattern
Use the agentic workflow: Solution Designer → BA → Coding Agent

1. **Solution Designer**: Creates architecture, tool inventory, handoff envelope
2. **BA**: Creates spec, tasklist (30-120 min tasks), rules.yaml, quality gates
3. **Coding Agent**: Implements tasks in dependency order with TDD

### Artifacts Produced
```
project_v2_solution_design.md  # Architecture + handoff envelope
project_v2_spec.md             # Requirements
project_v2_tasklist.md         # Dependency-ordered tasks
project_v2_rules.yaml          # Runtime configuration
project_v2_quality_gates.md    # Evidence requirements
project_v2_decisions.md        # Architectural decisions
project_v2_evolution.md        # Drift tracking
```

### Checklist
- [ ] Run design before BA for new feature sets
- [ ] Ensure tasklist tasks are 30-120 minutes each
- [ ] Include TDD evidence requirements per task
- [ ] Commit after each phase completion

---

## 26. tiktoken for Accurate Token Estimation

**Date**: 2026-01-17
**Project**: Bureaucrat MCP Server v2

### Problem
Estimating response token counts for MCP tools to enforce budgets.

### Pattern
Use tiktoken with cl100k_base encoding (GPT-4/Claude compatible).

```python
import tiktoken

_encoding = None

def estimate_tokens(text: str) -> int:
    global _encoding
    if _encoding is None:
        _encoding = tiktoken.get_encoding("cl100k_base")
    return len(_encoding.encode(text))
```

### Key Points
- Lazy-load tiktoken to avoid startup overhead
- cl100k_base is compatible with GPT-4 and Claude
- Accurate to within ~5% of actual token count
- Add to dependencies: `tiktoken>=0.5.0`

### Checklist
- [ ] Lazy-load encoding to avoid import overhead
- [ ] Use cl100k_base for modern LLM compatibility
- [ ] Cache encoding instance globally

---

## 27. datetime.utcnow() Deprecation

**Date**: 2026-01-17
**Project**: Bureaucrat MCP Server v2

### Problem
`datetime.utcnow()` is deprecated in Python 3.12+ and produces warnings.

### Pattern
Use timezone-aware datetime with `datetime.now(timezone.utc)`.

```python
# BAD - deprecated
from datetime import datetime
created_at = datetime.utcnow()

# GOOD - timezone-aware
from datetime import datetime, timezone
created_at = datetime.now(timezone.utc)
```

### Checklist
- [ ] Replace all datetime.utcnow() with datetime.now(timezone.utc)
- [ ] Import timezone from datetime module
- [ ] Use timezone-aware defaults in dataclass fields

---

## 28. Claude Code Permissions Configuration

**Date**: 2026-01-17
**Project**: Claude Code CLI Configuration

### Problem
Claude Code prompts for permission on every bash command by default, slowing down development workflows. Need to configure auto-approval for safe commands while protecting against dangerous operations.

### Pattern
Configure `~/.claude/settings.local.json` with three permission tiers.

```json
{
  "permissions": {
    "allow": ["Bash(safe-command:*)"],
    "ask": ["Bash(risky-command:*)"],
    "deny": ["Bash(dangerous-command:*)"]
  }
}
```

### Permission Tiers

| Tier | Behavior | Use For |
|------|----------|---------|
| `allow` | Auto-approved, no prompt | Read-only ops, builds, tests, linting |
| `ask` | Prompts before running | Destructive ops, publishing, remote changes |
| `deny` | Blocked entirely | rm -rf, chmod 777, reading .env files |

### Risk Categorization for Commands

**Safe for `allow` (auto-approve):**
- **Read-only**: git status/diff/log, ls, cat, grep, find
- **Builds**: npm run build, cargo build, go build
- **Tests**: pytest, npm test, cargo test
- **Linting**: ruff, mypy, eslint, prettier
- **Package info**: pip list, npm ls, npm outdated

**Move to `ask` (prompt first):**
- **Container destruction**: docker rm, docker rmi, docker stop
- **History rewriting**: git rebase
- **Database access**: psql, mysql, mongosh, redis-cli
- **Publishing**: npm publish, docker push, git push

**Always `deny`:**
- **Recursive deletion**: rm -rf, sudo rm
- **Insecure permissions**: chmod 777
- **Secret exposure**: Read(.env*)

### Session Statistics (2026-01-17)

| Metric | Value |
|--------|-------|
| Commands added to allow | 68 |
| Commands added to ask | 8 |
| Total allow rules | 164 |
| Categories covered | Git, Docker, Python, Node, Rust, Go, Cloud, Utilities |

### Commands Added by Category

**Git Extended:**
- git show, merge, tag, remote, cherry-pick, reset --soft/--mixed, clean -n, rev-parse, blame

**Docker Extended:**
- docker images, exec, network, volume, inspect, pull, start
- *Moved to ask*: docker rm, docker rmi, docker stop

**Python/Linting:**
- black, isort, bandit, pylint, flake8, coverage, python, python -m, pip list/show

**Node/JS Extended:**
- yarn, pnpm, npm ci/outdated/ls/audit, eslint, prettier, tsc, vitest, vite, next

**Rust:**
- cargo build/test/run/check/clippy/fmt, rustfmt

**Go:**
- go build/test/run/mod/fmt/vet

**Utilities:**
- jq, yq, diff, sort, uniq, cut, xargs, du, df, stat, file
- basename, dirname, realpath, date, env
- tar, zip/unzip, gzip/gunzip
- openssl, base64, md5, shasum

**Cloud/Deploy:**
- fly (all), vercel, netlify
- kubectl get/describe/logs (read-only)
- terraform plan/fmt

**System Info:**
- whoami, hostname, uname, lsof, ps, netstat, dig, nslookup, ping

### Checklist
- [ ] Start with read-only and build commands in `allow`
- [ ] Move destructive container ops (rm, rmi, stop) to `ask`
- [ ] Move database clients to `ask` if connecting to production
- [ ] Move git rebase to `ask` (history rewriting)
- [ ] Always deny rm -rf, chmod 777, reading .env files
- [ ] Review and extend as workflow needs evolve
- [ ] Restart Claude Code session after config changes

### Evidence
`~/.claude/settings.local.json` - 164 allow rules, 12 ask rules, 5 deny rules

---

## 29. Claude Code Directory Access Permissions

**Date**: 2026-01-17
**Project**: Claude Code CLI Configuration

### Problem
Claude Code has **two separate permission layers**:
1. **Bash command permissions** - whether a command (e.g., `mkdir`) can execute
2. **Directory access permissions** - which paths Claude can read/write/create files in

Having `Bash(mkdir:*)` allowed doesn't mean Claude can create directories anywhere. Directory write access must be granted separately.

### The Two Permission Layers

| Layer | Controls | Example Rule |
|-------|----------|--------------|
| Bash commands | Which shell commands run | `Bash(mkdir:*)`, `Bash(git:*)` |
| Directory access | Where files can be created/edited | `Write(~/Documents/**)` |

### Permission Types for Directory Access

```json
{
  "permissions": {
    "allow": [
      "Read(~/code/**)",           // Read files anywhere in ~/code
      "Write(~/code/**)",          // Create new files/directories
      "Edit(~/code/**)",           // Modify existing files
      "Write(/tmp/**)",            // Allow temp file creation
    ]
  }
}
```

### Scope Differences

| Scope | Storage Location | Use Case |
|-------|------------------|----------|
| Global | `~/.claude/settings.local.json` | Your personal defaults |
| Project | `<project>/.claude/settings.json` | Project-specific overrides |
| Session | In-memory only | One-time approvals (option 1) |

When you select **"Yes, and always allow access to X from this project"**, it stores in the project's `.claude/settings.json`, not globally.

### Risk Assessment for Common Directory Operations

| Operation | Risk Level | Recommendation |
|-----------|------------|----------------|
| `mkdir -p` | None | Always allow - only creates dirs |
| `Write(~/Documents/**)` | Low | Allow for dev folders |
| `Write(~/Desktop/**)` | Low | Allow if you work there |
| `Write(~/**)` | Medium | Too broad - could create anywhere |
| `Write(/**)` | High | Never - could write to system dirs |
| `Write(/etc/**)` | Critical | Deny - system configuration |

### Configuration Pattern

```json
{
  "permissions": {
    "allow": [
      "Write(~/Documents/**)",
      "Write(~/code/**)",
      "Write(~/projects/**)",
      "Edit(~/Documents/**)",
      "Edit(~/code/**)",
      "Edit(~/projects/**)"
    ],
    "deny": [
      "Write(/etc/**)",
      "Write(/usr/**)",
      "Write(/System/**)",
      "Read(.env*)"
    ]
  }
}
```

### Checklist
- [ ] Identify your development directories (Documents, code, projects, etc.)
- [ ] Add Write + Edit permissions for each development directory
- [ ] Use `**` glob for recursive access
- [ ] Never allow Write to root (`/**`) or system directories
- [ ] Restart Claude Code session after config changes
- [ ] When moving development folders, run migration prompt to update paths

### Evidence
Session 2026-01-17: `mkdir -p` command allowed but still prompted due to missing `Write()` permission for directory.

---

## 30. Quality Adapters: Subprocess Runners with Path Validation & Summarization

**Date**: 2026-01-17
**Project**: Bureaucrat MCP v2

### Context
Implemented three quality adapters (PytestAdapter, CodeQualityAdapter, SecurityScannerAdapter) that wrap CLI tools via subprocess with consistent patterns for security and token efficiency.

### Lessons

#### 30.1 Test Directory Naming Collision
**Problem**: Creating `tests/unit/components/adapters/pytest/` directory caused import collision with the `pytest` module.
```
ModuleNotFoundError: No module named 'pytest.test_adapter'
```

**Solution**: Use `_adapter` suffix for test directories that share names with Python packages:
- `pytest_adapter/` instead of `pytest/`
- `code_quality/` (safe - no collision)
- `security_scanner/` (safe - no collision)

**Checklist**:
- [ ] Before creating test directories, check if name collides with installed packages
- [ ] Use `_adapter` or `_tests` suffix when name matches a package

#### 30.2 Path Validation Pattern (CTRL-111)
**Requirement**: All file/directory accepting adapters must validate paths to prevent traversal attacks.

**Canonical Implementation**:
```python
def _validate_path(path: str, base_dir: str | None = None) -> tuple[bool, str]:
    try:
        resolved = Path(path).resolve()
        if ".." in path:
            return False, "Path traversal not allowed"
        if base_dir:
            base_resolved = Path(base_dir).resolve()
            if not str(resolved).startswith(str(base_resolved)):
                return False, "Path outside allowed directory"
        if not resolved.exists():
            return False, f"Path does not exist: {path}"
        return True, ""
    except Exception as e:
        return False, f"Invalid path: {e}"
```

**Return Pattern**: `tuple[bool, str]` for clear error handling.

#### 30.3 Finding/Violation Summarization Strategy
**Goal**: Keep MCP responses token-efficient (<200 tokens target, <500 hard limit).

**Pattern**:
1. Aggregate results into maps: `by_rule: dict[str, int]`, `by_file: dict[str, int]`, `severity_counts`
2. Limit detailed items: `MAX_FAILURES=10`, `MAX_VIOLATIONS=20`, `MAX_FINDINGS=20`
3. Threshold for summary mode: `SUMMARIZE_THRESHOLD=50` triggers compact format
4. Summary always truncated: `summary[:140]`

**Summary Format Examples**:
```python
# Under threshold
"5 violations found"
# Over threshold
"100 violations (top: E501: 50, F401: 30, W291: 20)"
# Security
"100 findings (C:10 H:20 M:30 L:40)"
```

#### 30.4 Stub Adapter Pattern for Testing
**Every adapter must have a `Stub{Adapter}` implementation** for testing without external tools.

**Required Features**:
1. Configurable result: `__init__(result: Result | None = None)`
2. Configurable exception: `__init__(exception: Exception | None = None)`
3. Call tracking: `self.{method}_calls: list[dict[str, Any]]`

**Template**:
```python
class StubFooAdapter:
    def __init__(
        self,
        result: FooResult | None = None,
        exception: Exception | None = None,
    ):
        self._result = result or FooResult(success=True)
        self._exception = exception
        self.run_calls: list[dict[str, Any]] = []

    def run(self, path: str, **kwargs) -> FooResult:
        self.run_calls.append({"path": path, **kwargs})
        if self._exception:
            raise self._exception
        return self._result
```

#### 30.5 Atomic Component Entry Point Standard
**Signature Pattern**:
```python
def run_{action}(
    inp: {Action}Input,
    *,  # Keyword-only for DI
    adapter: {Adapter}Port,
) -> {Action}Output:
```

**Requirements**:
- Input/Output models: Pydantic with `model_config = {"frozen": True}`
- Port: Python Protocol class for dependency injection
- Summary always truncated: `return Output(summary=summary[:140], ...)`

### File References
- Pattern source: `src/bureaucrat_mcp/components/adapters/pytest/component.py`
- Pattern source: `src/bureaucrat_mcp/components/adapters/code_quality/component.py`
- Pattern source: `src/bureaucrat_mcp/components/adapters/security_scanner/component.py`

### Evidence
Session 2026-01-17: 615 tests passing after implementing 3 quality adapters with 95 new tests.

---

## 31. Governance Drift via Atomic Component Drift

### Lesson: Silent Structural Drift Accumulates When No Per-Task Validation Exists

**Project**: Bureaucrat MCP v2 (2026-01-17)

**What happened:**

During Bureaucrat MCP v2 development, 8 new components were implemented and functionally complete (code + tests + git history). However:
- 6 adapters had NO contract.md files (docker, github, flyio, pytest, code_quality, security_scanner)
- 1 component (result_summarizer) had NO ports.py file
- 0 of 8 components were registered in component_manifest.json
- Quality gates did not check for atomic component structure
- Unused imports accumulated (caught only at end-of-phase audit)
- Test expectations drifted (expected 10 components, found 18)

Coding agent implemented features task-by-task without detecting structural gaps because:
1. Atomic component checklist was mentioned in system prompt but not enforced as a GATE
2. No pre-implementation structural validation (files could be missing without immediate feedback)
3. Manifest update was not a task AC, only mentioned generically in spec
4. Quality gate script had no component structure validation (only code style + types)

**Time cost:** ~8 hours of remediation to:
1. Create 6 missing contract.md files
2. Create 1 missing ports.py file
3. Register 8 components in manifest
4. Upgrade quality gate script with G3 (manifest validation)
5. Fix unused imports and type errors
6. Update test expectations

**Root cause:** No **hard enforcement** between tasks. Coding agent could complete multiple tasks without triggering atomic component structure validation.

### Prevention Strategy (Updated Coding Agent + BA):

**BA Responsibility:**
- Include explicit manifest update AC in every component creation task
- Quality gate spec must include component structure validation (contract.md, ports.py existence checks)
- Define expected manifest entry format in rules.yaml

**Coding Agent Responsibility:**
- Before any implementation: Create ALL atomic component files (stubs OK, but files must exist)
- Create component.py (empty run() function is OK)
- Create contract.md with at least Purpose + Input/Output sections
- Create ports.py (even if empty)
- Add manifest entry immediately (status: "in_progress")
- After task completion: Quality gate validates component structure exists, updates manifest status to "complete"

**Quality Gate Script Responsibility:**
- G3_manifest_validation must check:
  - All components in manifest exist on filesystem
  - Each component has required files: component.py, models.py, ports.py, contract.md
  - No phantom components (code exists but not in manifest)
  - Manifest metadata is valid JSON + required fields populated

### Checklist for Future Projects:

- [ ] **Before first component:** Write component structure validation gate (G3 or equivalent)
- [ ] **Before each component task:** Create stubs for all atomic files (contract.md first!)
- [ ] **After each task:** Verify manifest entry exists and status is updated
- [ ] **During BA planning:** Include manifest update as AC in component creation tasks
- [ ] **Quality gate verification:** Run atomic compliance check per-task, not just end-of-phase
- [ ] **Manifest.json spec:** Define required fields (name, path, type, purpose, status, contract_path, task_id)

### Agent Prompt Changes Recommended:

**Coding Agent System Prompt** — Add "Prime Directive Check" step:
```markdown
Component Structure Validation (REQUIRED BEFORE IMPLEMENTATION):
- [ ] Does this task create or modify a component?
- [ ] If YES, before writing ANY code:
  - [ ] Atomic component directory exists
  - [ ] component.py, models.py, ports.py, contract.md, __init__.py stubs exist
  - [ ] Component entry added to manifest with status: "in_progress"
- [ ] Quality gates include check for missing files
```

**BA Agent Prompt** — Add Manifest Update Task Pattern:
```markdown
For each new component task:
- AC: All atomic files present (component.py, models.py, ports.py, contract.md, tests)
- AC: Manifest entry added with complete metadata
- AC: Quality gate G3 (manifest validation) passes
```

### Related Decisions:
- EV-0002, EV-0003: Bureaucrat v2 governance remediation trail
- D-01 through D-04: Deviation catalog from remediation.md

---

## 32. Browser Automation with Playwright

### Lesson: Use persistent context and appropriate load states for stateful web apps

**Project**: Bureaucrat MCP v2 - NotebookLM Adapter
**Date**: 2026-01-18

**What happened:**
When building browser automation for NotebookLM, we encountered several key challenges:

1. **Session persistence**: NotebookLM requires Google authentication. Fresh browser instances would require login on every run.
2. **Load state issues**: Using `networkidle` caused timeouts because NotebookLM maintains persistent WebSocket connections for collaboration features.
3. **Modal overlays**: Unpredictable promotional dialogs and tooltips blocked interactions.
4. **State contamination**: After generating one artifact, UI state (open viewers, selected items) affected subsequent operations.

**Solutions implemented:**

```python
# 1. Persistent context for session reuse
context = await playwright.chromium.launch_persistent_context(
    user_data_dir=str(config.profile_dir),
    headless=config.headless,
    args=["--disable-blink-features=AutomationControlled"],  # Avoid bot detection
)

# 2. Use domcontentloaded, not networkidle, for apps with persistent network activity
await page.goto(url)
await page.wait_for_load_state("domcontentloaded")
await page.wait_for_timeout(3000)  # Allow UI rendering

# 3. Layered overlay dismissal strategy
async def _dismiss_overlays(self, max_attempts: int = 5):
    for attempt in range(max_attempts):
        for btn_text in ["Got it", "Close", "Skip", "Dismiss"]:
            btn = page.locator(f"button:has-text('{btn_text}')").first
            if await btn.count() > 0:
                await btn.click(force=True)
                break
        await page.keyboard.press("Escape")  # Fallback

# 4. Page reload between operations to reset state
await page.reload(wait_until="domcontentloaded")
await page.wait_for_timeout(3000)
```

### Future Checklist:
- [ ] Use `launch_persistent_context()` when session state must survive restarts
- [ ] Store profile directory outside project (e.g., `~/.app-automation/`)
- [ ] Add `--disable-blink-features=AutomationControlled` to avoid bot detection
- [ ] Check Network tab: Does app have WebSocket/polling? If YES → use `domcontentloaded`
- [ ] Call overlay dismissal before critical interactions
- [ ] Reload page between sequential long operations to reset UI state
- [ ] Use `expect_download()` BEFORE clicking download button
- [ ] Set timeouts appropriate to operation type (audio generation: 10min, static export: 2min)

---

## 33. Selector Versioning for Dynamic Web Apps

### Lesson: Centralize all UI selectors in a single file with version metadata

**Project**: Bureaucrat MCP v2 - NotebookLM Adapter
**Date**: 2026-01-18

**What happened:**
NotebookLM's UI undergoes frequent updates. Selectors that worked one week would break the next. Without centralized management:
- Duplicate selectors scattered across browser.py methods
- No way to track when selectors were last verified
- Debugging "selector not found" errors was time-consuming

**Solution:**
Created `selectors.py` with versioned, centralized selectors:

```python
"""
NotebookLM UI Selectors.
Version: 2026-01-18
Last Verified: 2026-01-18
Note: Selectors verified on NotebookLM 2026-01 UI refresh
"""

SELECTORS: Dict[str, str] = {
    "new_notebook_button": "button[aria-label='Create new notebook']",
    "studio_tab": "button[role='tab']:has-text('Notebook Guide')",
    "artifact_audio_overview_card": ".create-artifact-button-container:has-text('Audio Overview')",
    # ... more selectors
}

def get_selector(key: str) -> str:
    """Retrieve selector, raise SelectorError if missing."""
    if key not in SELECTORS:
        raise SelectorError(key, "UNKNOWN", "Selector key not found")
    return SELECTORS[key]

def validate_selectors() -> List[str]:
    """Return list of invalid selector keys."""
    return [k for k, v in SELECTORS.items() if not v.strip()]
```

### Future Checklist:
- [ ] Create `selectors.py` before writing browser automation code
- [ ] Add version date comment with "Last Verified" timestamp
- [ ] Use semantic keys: `"add_source_button"` not `"button_123"`
- [ ] Include validation function in unit tests
- [ ] Document fallback strategies in comments
- [ ] When selectors break, update version date and verify all selectors

---

## 34. Hardcoded Paths in Development Code

### Lesson: Never commit hardcoded absolute paths - use config or relative paths

**Project**: Bureaucrat MCP v2 - NotebookLM Adapter
**Date**: 2026-01-18

**What happened:**
During rapid development, hardcoded paths crept into browser.py:
```python
# BAD - breaks on any other machine
save_dir = Path("/Users/naidooone/Developer/projects/thatcher/artifacts/notebooklm/temp")
debug_path = Path("/Users/naidooone/Developer/projects/thatcher/artifacts/notebooklm/debug")
```

This was flagged by QA review. The code would fail:
- When deployed to production
- When run by other developers
- When run in containers

**Solution:**
Added `artifact_dir` to config and used it throughout:

```python
# models.py
@dataclass
class NotebookLMConfig:
    profile_dir: Path
    artifact_dir: Optional[Path] = None  # Directory for generated artifacts

    def __post_init__(self) -> None:
        if self.artifact_dir is None:
            # Default to artifacts/{subdir} in current working directory
            self.artifact_dir = Path.cwd() / "artifacts" / self.artifact_subdir

# browser.py - GOOD
save_dir = self.config.artifact_dir / "temp"
debug_path = self.config.artifact_dir / "debug"
```

### Future Checklist:
- [ ] Never use absolute paths with username in code
- [ ] Add path fields to config dataclass with sensible defaults
- [ ] Use `Path.cwd()` or `Path(__file__).parent` for relative paths
- [ ] Run `grep -r "/Users/" src/` before committing to catch hardcoded paths
- [ ] QA review should flag absolute paths as FAIL
- [ ] For debug screenshots, use configurable artifact directory

---

## 35. QA Remediation Session Analysis & Drift Detection Metrics

**Date**: 2026-01-18
**Project**: Little Research Lab
**Context**: Compliance remediation session following compliance_report_v1.md audit

### Session Statistics

| Metric | Value | Notes |
|--------|-------|-------|
| **Conversation Turns** | 22 | User prompts + assistant responses |
| **Tool Calls Made** | 47 | Read, Edit, Bash, Grep, Glob, Task, TodoWrite |
| **Files Read** | 18 | Including ports.py, component.py, models.py across 3 components |
| **Files Directly Modified** | 8 | component.py, models.py, ports.py for Newsletter, Engagement, Collaboration |
| **Directories Relocated** | 3 | core → domain/core, shell → app_shell/shell, api → app_shell/api |
| **Import Statements Updated** | 59+ | Via sed find-and-replace |
| **Lines of Code Added** | ~80 | New port definitions, constructor params |
| **Lines of Code Modified** | ~120 | Function signatures, import statements |
| **Tests Written** | 0 | Tests not updated (discovered post-QA) |

### Drift Detection Timeline

**Turn 1-3**: Initial compliance report analysis
- Scope identified: 4 tasks (MST-001 through MST-004)
- Apparent scope: Component-level determinism + directory structure

**Turn 4-15**: Core remediation work
- Newsletter TimeProvider/UUIDProvider injection
- Engagement TimePort made required
- Collaboration UUIDProvider injection
- All changes scoped to `src/components/`

**Turn 16-19**: Directory structure remediation
- Moved 3 directories
- Updated 59+ import statements
- Manifest check PASS achieved

**Turn 20-22**: QA review revealed hidden scope
- **25+ additional violations discovered** in `src/domain/core/`
- 15 newsletter tests broken (signatures changed, tests not updated)
- Original compliance report scope was **incomplete**

### When Code Drift / Quality Degradation Occurred

**Critical Finding**: The original compliance report only audited `src/components/` but the codebase has TWO locations with business logic:
1. `src/components/` (atomic pattern) - AUDITED
2. `src/domain/core/services/` (legacy pattern) - NOT AUDITED

**Drift Point**: Turn 16 - Directory moves completed without realizing domain/core services also had determinism violations

**Root Cause Analysis**:
```
┌─────────────────────────────────────────────────────────────┐
│ Compliance Report Scope: src/components/*                    │
│ Actual Violation Scope: src/components/* + src/domain/core/* │
│                                                              │
│ Gap: 25+ violations in domain/core not in original report   │
└─────────────────────────────────────────────────────────────┘
```

### Objective Metrics for Detecting Context Drift

**Recommendation**: Implement these automated checks BEFORE any remediation task:

#### 1. Violation Coverage Check
```bash
# Count violations ACROSS ENTIRE CODEBASE, not just reported scope
datetime_violations=$(grep -r "datetime\.\(utcnow\|now\)" src/ --include="*.py" | grep -v test | grep -v adapter | wc -l)
uuid_violations=$(grep -r "uuid\.uuid4\(\)" src/ --include="*.py" | grep -v test | grep -v adapter | wc -l)

# Compare against compliance report count
# DRIFT SIGNAL: If actual > reported, scope is incomplete
```

**This Session**: Report identified 7 datetime violations, actual count was 32+

#### 2. Test Signature Sync Check
```bash
# After any function signature change, verify test compatibility
python -c "import pytest; pytest.main(['--collect-only', '-q'])" 2>&1 | grep -c "error"
# DRIFT SIGNAL: If errors > 0, tests need updating
```

**This Session**: 15 tests broken, not caught until QA review

#### 3. Architecture Layer Audit
```bash
# Check ALL layers for violations, not just one
for layer in components domain adapters services; do
  echo "=== $layer ==="
  grep -r "datetime\.\(utcnow\|now\)" src/$layer/ --include="*.py" 2>/dev/null | grep -v test | wc -l
done
# DRIFT SIGNAL: Non-zero in core layers (components, domain, services)
```

#### 4. Scope Expansion Metric
```
Original Task Count: N
Discovered Task Count After QA: M
Scope Expansion Ratio: M / N

This Session: 4 original / 4+ (25+ hidden) = 7.25x scope expansion
DRIFT SIGNAL: Ratio > 1.5x indicates incomplete initial analysis
```

### Quality Degradation Signals

| Signal | Threshold | This Session | Status |
|--------|-----------|--------------|--------|
| Violation coverage mismatch | Report vs Actual > 10% | 7 vs 32+ (357% gap) | FAIL |
| Broken tests after refactor | > 0 | 15 | FAIL |
| Scope expansion ratio | > 1.5x | 7.25x | FAIL |
| Layers with violations | > 1 (only adapters OK) | 3 layers | FAIL |
| Import update completeness | 100% | 100% | PASS |
| Manifest check | PASS | PASS | PASS |

### Lessons Learned

#### Lesson 35a: Compliance Reports Must Audit ENTIRE Codebase
**Problem**: Compliance report scoped to `src/components/` missed 25+ violations in `src/domain/core/`

**Evidence**:
- Report: 4 datetime.now() violations (Newsletter, Engagement, Collaboration)
- Reality: 32+ violations (above + 25+ in domain/core/services)

**Quality Gate**:
```bash
# BEFORE accepting compliance report
total_violations=$(grep -r "datetime\.\(utcnow\|now\)" src/ --include="*.py" | grep -v test | grep -v adapter | wc -l)
echo "Total codebase violations: $total_violations"
# Report must account for ALL $total_violations
```

#### Lesson 35b: Test Signature Sync is Mandatory Post-Refactor
**Problem**: Changed 4 function signatures, didn't update 15 tests

**Impact**:
- Cannot verify refactored code works correctly
- False confidence from "remediation complete" status

**Quality Gate**:
```bash
# AFTER any signature change
pytest --collect-only 2>&1 | grep -i error && echo "FAIL: Tests need signature updates"
pytest --tb=short 2>&1 | head -50  # Quick smoke test
```

#### Lesson 35c: Layer Audit Before Layer Remediation
**Problem**: Fixed components layer, didn't realize domain/core also needed fixes

**Pattern**: In hexagonal architecture, determinism violations can exist in:
1. `src/components/` (functional core - atomic pattern)
2. `src/domain/` (functional core - traditional pattern)
3. `src/services/` (may be core or shell depending on project)

**Quality Gate**:
```bash
# Audit ALL potential core layers
for dir in components domain services core; do
  violations=$(grep -r "datetime\.\(utcnow\|now\)\|uuid\.uuid4\(\)" src/$dir/ --include="*.py" 2>/dev/null | grep -v test | wc -l)
  if [ "$violations" -gt 0 ]; then
    echo "WARN: $dir has $violations determinism violations"
  fi
done
```

### Recommended Workflow Changes

#### Pre-Remediation Checklist
```markdown
Before accepting a compliance report as complete scope:

- [ ] Run `grep -r "datetime\.\(utcnow\|now\)" src/ --include="*.py" | grep -v test | grep -v adapter | wc -l`
- [ ] Verify count matches report (±10% tolerance)
- [ ] Audit ALL layers: components, domain, services, core
- [ ] Document any layers explicitly OUT OF SCOPE with justification
```

#### Post-Remediation Checklist
```markdown
After completing remediation tasks:

- [ ] Run pytest collection: `pytest --collect-only 2>&1 | grep error`
- [ ] Run quick test: `pytest --tb=short -x` (stop on first failure)
- [ ] Re-run original violation grep to verify count = 0
- [ ] QA review with explicit "check for hidden scope" instruction
```

### Future Checklist
- [ ] Compliance reports must include total violation count across entire src/
- [ ] Test signature sync check after EVERY function signature change
- [ ] Audit ALL core layers (components, domain, services) not just one
- [ ] Calculate scope expansion ratio after QA review
- [ ] If ratio > 1.5x, halt and expand original scope before continuing
- [ ] Never mark remediation "complete" without passing tests

### Statistics Template for Future Sessions

```markdown
## Session: [DATE] - [TOPIC]

| Metric | Value |
|--------|-------|
| Conversation Turns | |
| Tool Calls | |
| Files Modified | |
| Lines Changed | |
| Tests Written/Updated | |
| Original Scope | |
| Final Scope | |
| Scope Expansion Ratio | |
| Broken Tests Discovered | |
| Hidden Violations Found | |
| Time to Complete | |
```

---

## Lesson 36: Quality Gates Artifact Files Can Exceed Context Limits

**Date**: 2026-01-18
**Project**: research_lab (audience growth)
**Severity**: Medium (workflow blocker)

### Context

During quality gates verification for T-C011 (resolve_comment), the `quality_gates_run.json` artifact file had grown to 77,591 tokens (240KB), far exceeding Claude's 25,000 token read limit. This blocked the standard quality gates workflow because:

1. The Write tool requires reading the file first before writing
2. The Read tool has a 25,000 token limit
3. pytest JSON reports accumulate detailed test information that grows with each run

### Symptoms

```
Error: File content (77591 tokens) exceeds maximum allowed tokens (25000)
```

When attempting to update `artifacts/quality_gates_run.json` with new quality gate results.

### Root Cause

Quality gates artifacts accumulate over time:
- Multiple pytest JSON reports appended to single file
- Detailed test metadata (fixtures, durations, assertions) bloats file size
- No cleanup or rotation strategy for artifact files

### Lesson: Keep Quality Gates Artifacts Small and Separate

**DO:**
- Use separate files per quality gate run: `{component}_quality_report_{timestamp}.json`
- Keep summary files small (~5-10KB), link to detailed pytest JSON reports
- Archive or rotate old reports periodically
- Use Bash with heredoc/cat for creating new files (bypasses Read requirement)

**DON'T:**
- Accumulate all quality gate results in a single monolithic file
- Store full pytest JSON output in summary files
- Assume artifact files will remain readable over long sessions

### Recommended Artifact Structure

```
artifacts/
├── quality_gates_summary.json          # <10KB, current status only
├── pytest-{component}-{date}.json      # Detailed per-run reports
├── archive/                            # Old reports (>7 days)
│   └── pytest-collaboration-20260111.json
```

### Quality Gates Summary Schema (Keep Small)

```json
{
  "last_run": "2026-01-18T22:07:00Z",
  "component": "collaboration",
  "tests": { "passed": 195, "failed": 0 },
  "linting": "pass",
  "typing": "pass_with_warnings",
  "gate_result": "PASS",
  "detailed_report": "artifacts/pytest-collaboration-20260118.json"
}
```

### Mitigation Workaround

When you hit the limit:
```bash
# Use Bash to create new file (bypasses Read requirement)
cat > artifacts/new_quality_report.json << 'EOF'
{ "your": "data" }
EOF
```

### Prevention Checklist

- [ ] Quality gates summary files < 10KB
- [ ] Detailed pytest output in separate timestamped files
- [ ] Archive reports older than 7 days
- [ ] Never append to quality gates files - overwrite summary, create new detailed

---

## Lesson 37: BA Artifacts May Be Gitignored - Check Before Committing

**Date**: 2026-01-18
**Project**: research_lab (audience growth)
**Severity**: Low (workflow awareness)

### Context

After completing quality gates and updating the evolution log (`research_lab_audience_growth_evolution.md`), attempted to commit the changes. Git rejected the BA artifact files because they matched gitignore patterns.

### Symptoms

```bash
$ git add research_lab_audience_growth_*.md
The following paths are ignored by one of your .gitignore files:
research_lab_audience_growth_evolution.md
hint: Use -f if you really want to add them.
```

### Root Cause

The project's `.gitignore` contains patterns that exclude BA artifacts:
```
.gitignore:117:*_evolution.md
```

This is intentional - BA artifacts (spec, tasklist, evolution, decisions) are often:
- Generated/managed by BA agents
- Contain project-specific context not needed in version control
- May contain sensitive planning information
- Updated frequently during development (noisy commits)

### Lesson: Verify BA Artifact Git Status Before Workflow

**BEFORE updating BA artifacts:**
1. Check if they're gitignored: `git check-ignore -v <filename>`
2. If ignored, updates are local-only (not version controlled)
3. If needed in git, use `git add -f` or update `.gitignore`

**BA artifacts commonly gitignored:**
- `*_evolution.md` - Drift/change logs
- `*_tasklist.md` - Task tracking
- `*_spec.md` - Requirements (sometimes)
- `*_decisions.md` - Architecture decisions

**BA artifacts commonly tracked:**
- `CLAUDE.md` - Project instructions
- `README.md` - Documentation
- Solution design documents

### Verification Commands

```bash
# Check if file is ignored
git check-ignore -v research_lab_audience_growth_evolution.md

# See all ignored files in directory
git status --ignored

# Force add if needed (override gitignore)
git add -f research_lab_audience_growth_evolution.md
```

### Recommendation

If evolution logs contain valuable project history that should be preserved:
1. Remove the `*_evolution.md` pattern from `.gitignore`
2. Or use a different naming convention: `EVOLUTION.md` (no underscore pattern)
3. Or accept that evolution logs are ephemeral session artifacts

---

## Lesson 38: TipTap Custom Extension Pattern for Rich Attributes

**Date**: 2026-01-19
**Project**: research_lab (audience growth)
**Severity**: Medium (architecture pattern)

### Context

Needed to create custom TipTap nodes for:
1. **CodeBlock** - with language, filename, lineNumbers, highlightLines, theme attributes
2. **ImagePlacement** - with placement (teaser/header/explainer/gallery), alt, caption, credit attributes

StarterKit includes basic CodeBlock but lacks the rich attributes needed for the spec.

### Problem

TipTap's built-in extensions don't support custom metadata. Attempted approaches:
- Extending built-in extensions - complex inheritance issues
- Using attrs on built-in nodes - limited attribute support

### Solution: Custom Node.create() with Full Attribute Schema

**Pattern for custom TipTap extensions:**

```typescript
// components/editor/extensions/CodeBlockExtension.ts
import { Node, mergeAttributes } from "@tiptap/core"

export const CodeBlockExtension = Node.create({
    name: "codeBlockCustom",  // Unique name to avoid conflicts

    content: "text*",
    marks: "",
    group: "block",
    code: true,
    defining: true,

    addAttributes() {
        return {
            language: {
                default: "plaintext",
                parseHTML: (element) => element.getAttribute("data-language") || "plaintext",
                renderHTML: (attributes) => ({ "data-language": attributes.language }),
            },
            filename: {
                default: null,
                parseHTML: (element) => element.getAttribute("data-filename"),
                renderHTML: (attributes) => attributes.filename ? { "data-filename": attributes.filename } : {},
            },
            // ... more attributes
        }
    },

    parseHTML() {
        return [{ tag: "pre", preserveWhitespace: "full" }]
    },

    renderHTML({ node, HTMLAttributes }) {
        return ["pre", mergeAttributes(HTMLAttributes), ["code", {}, 0]]
    },

    addCommands() {
        return {
            setCodeBlock: (attributes) => ({ commands }) =>
                commands.setNode(this.name, attributes),
            toggleCodeBlock: (attributes) => ({ commands }) =>
                commands.toggleNode(this.name, "paragraph", attributes),
        }
    },
})
```

### Critical Integration Steps

**1. Disable conflicting StarterKit extensions:**
```typescript
// RichTextEditor.tsx
StarterKit.configure({
    codeBlock: false,  // Disable when using custom CodeBlockExtension
}),
CodeBlockExtension,
```

**2. Update block-renderer for SSR:**
```typescript
// block-renderer.tsx - must include same extensions
const extensions = [
    StarterKit.configure({ codeBlock: false }),
    CodeBlockExtension,
    ImagePlacementExtension,
    Link.configure({ openOnClick: false }),
];
```

**3. TypeScript Commands Declaration:**
```typescript
declare module "@tiptap/core" {
    interface Commands<ReturnType> {
        codeBlockCustom: {
            setCodeBlock: (attributes?: {...}) => ReturnType
            toggleCodeBlock: (attributes?: {...}) => ReturnType
        }
    }
}
```

### Attribute Design Pattern

| Attribute Type | parseHTML | renderHTML |
|---------------|-----------|------------|
| Required | Return default if missing | Always emit |
| Optional | Return null if missing | Only emit if truthy |
| Boolean | Check for "false" string | Emit "true"/"false" |
| Enum | Validate against allowed values | Emit as data-attr |

### Files Created

```
components/editor/extensions/
├── index.ts                      # Re-exports all extensions
├── CodeBlockExtension.ts         # Code blocks with syntax highlighting attrs
└── ImagePlacementExtension.ts    # Images with placement metadata
```

### Prevention Checklist

- [ ] Always disable StarterKit's version when using custom extension
- [ ] Ensure parseHTML/renderHTML are symmetric (can round-trip)
- [ ] Export constants for allowed values (SUPPORTED_LANGUAGES, IMAGE_PLACEMENTS)
- [ ] Update both editor and renderer with same extensions
- [ ] Declare TypeScript Commands interface for type safety

---

## Lesson 39: shadcn/ui Component Dependencies Must Be Added Incrementally

**Date**: 2026-01-19
**Project**: research_lab (frontend)
**Severity**: Low (build errors)

### Context

When building the ImagePlacementModal, the build failed because referenced shadcn/ui components didn't exist:
- `@/components/ui/alert` - not installed
- `@/components/ui/radio-group` - not installed

### Problem

shadcn/ui is a "copy-paste" component library - components must be explicitly added to the project. Unlike npm packages, they don't exist until copied.

### Symptoms

```
Error: Turbopack build failed with 1 errors:
./components/editor/components/ImagePlacementModal.tsx:19:1
Module not found: Can't resolve '@/components/ui/alert'
```

### Solution

**Option 1: Use shadcn CLI (preferred)**
```bash
npx shadcn@latest add radio-group
npx shadcn@latest add alert
```

**Option 2: Manual creation (when CLI not available)**
```typescript
// components/ui/radio-group.tsx
import * as RadioGroupPrimitive from "@radix-ui/react-radio-group"
// ... implement component

// Also install the radix primitive:
npm install @radix-ui/react-radio-group
```

### Components Commonly Missing

| Component | Radix Dependency | Common Use |
|-----------|-----------------|------------|
| RadioGroup | @radix-ui/react-radio-group | Form selections |
| Alert | None (pure Tailwind) | Error/warning messages |
| AlertDialog | @radix-ui/react-alert-dialog | Confirmation modals |
| Accordion | @radix-ui/react-accordion | Collapsible sections |
| Checkbox | @radix-ui/react-checkbox | Form checkboxes |

### Prevention Checklist

- [ ] Before importing shadcn component, verify it exists in `components/ui/`
- [ ] Run `ls components/ui/` to see available components
- [ ] Install radix dependencies when creating components manually
- [ ] Keep a list of installed shadcn components in project docs

---

## Lesson 40: Image Placement Architecture - Storing Metadata in TipTap Nodes

**Date**: 2026-01-19
**Project**: research_lab (audience growth)
**Severity**: Medium (data architecture)

### Context

The spec requires images with placement metadata for:
- **Teaser**: Used for OpenGraph/social previews (first priority)
- **Header**: Full-width hero images
- **Explainer**: Inline explanatory images
- **Gallery**: Grid-based image collections

Backend `ImagePlacementService` extracts these for SSR rendering and OG tag generation.

### Problem

Standard TipTap Image extension only stores `src`, `alt`, `title`. Need to store placement type plus caption/credit for proper rendering.

### Solution: Custom ImagePlacement Node

**TipTap Extension Attributes:**
```typescript
addAttributes() {
    return {
        src: { default: null },
        alt: { default: "" },  // Required for accessibility
        placement: {
            default: "explainer",  // Safe default
            parseHTML: (el) => el.getAttribute("data-placement") || "explainer",
        },
        caption: { default: null },  // Optional figcaption
        credit: { default: null },   // Photo credit
        width: { default: null },
        height: { default: null },
    }
}
```

**HTML Output Structure:**
```html
<figure class="image-placement img-teaser" data-placement="teaser">
    <img src="..." alt="..." loading="lazy" />
    <figcaption>Caption text <span class="credit">(Photo by...)</span></figcaption>
</figure>
```

### Frontend-Backend Alignment

| Frontend (TipTap) | Backend (Python) | Purpose |
|-------------------|------------------|---------|
| `placement: "teaser"` | `ImagePlacementType.TEASER` | OpenGraph image |
| `placement: "header"` | `ImagePlacementType.HEADER` | Hero image |
| `alt` (required) | `ImageNode.alt` | Accessibility |
| `caption` | `ImageNode.caption` | Display text |
| `credit` | `ImageNode.credit` | Attribution |

### Modal Flow for Image Insertion

```
1. User clicks Image button in toolbar
2. ImagePlacementModal opens
3. User uploads image → AssetsService.uploadAsset()
4. User fills: alt (required), placement (radio), caption, credit
5. Modal calls editor.commands.setImagePlacement({...})
6. TipTap inserts imagePlacement node with all metadata
```

### CSS Classes for Placement-Specific Styling

```css
.img-teaser { max-width: 20rem; margin: auto; }
.img-header { width: 100%; max-height: 400px; object-fit: cover; }
.img-explainer { max-width: 42rem; margin: auto; }
.img-gallery { max-width: 15rem; display: inline-block; }
```

### SSR Rendering Flow

```
TipTap JSON → ImagePlacementService.parse_images() → ParsedImages
    → extract_teaser_image() → OpenGraphTags for <head>
    → render_image() → HTML with placement CSS classes
```

### Prevention Checklist

- [ ] Alt text is required (accessibility compliance)
- [ ] Default placement is "explainer" (safest for inline content)
- [ ] Caption/credit are optional
- [ ] Teaser image priority: explicit teaser > first image > generated fallback
- [ ] Placement CSS classes must match between frontend and backend

---

## Lesson 41: Prompt Library CRUD Pattern - Browse/Detail/Admin Architecture

**Date**: 2026-01-19
**Project**: research_lab (audience growth)
**Severity**: Low (UI pattern)

### Context

Built a complete Prompt Library feature with:
- Public browse page (`/prompts`)
- Public detail page (`/prompts/[slug]`)
- Admin list page (`/admin/prompts`)
- Admin create page (`/admin/prompts/new`)
- Admin edit page (`/admin/prompts/[id]`)

### Architecture Pattern

```
Public Routes (by slug)           Admin Routes (by ID)
/prompts          → browse        /admin/prompts       → list + filters
/prompts/[slug]   → read-only     /admin/prompts/new   → create form
                                  /admin/prompts/[id]  → edit form
```

### API Service Pattern

```typescript
// lib/api/services/PromptLibraryService.ts
export class PromptLibraryService {
    // Public endpoints (by slug)
    static getPromptBySlug(slug: string)
    static searchPrompts(q: string, limit?: number)
    static getAllTags()

    // Admin endpoints (by ID)
    static listPrompts(status?, tag?, limit?, offset?)
    static getPromptById(id: string)
    static createPrompt(request: CreatePromptRequest)
    static updatePrompt(id: string, request: UpdatePromptRequest)
    static publishPrompt(id: string)
    static archivePrompt(id: string)

    // Analytics
    static recordCopy(id: string)
}
```

### Status Workflow

```
draft → published → archived
  ↑                    ↓
  └────────────────────┘ (can unarchive)
```

### Component Organization

```
components/prompts/
├── TagCloud.tsx      # Tag cloud with frequency-based sizing
├── PromptSearch.tsx  # Debounced search with highlighting

app/prompts/
├── page.tsx          # Browse page (search + tag filter + grid)
└── [slug]/page.tsx   # Detail page (read-only, copy button)

app/admin/prompts/
├── page.tsx          # Admin list (table + status filter)
├── new/page.tsx      # Create form
└── [id]/page.tsx     # Edit form + publish/archive actions
```

### Key UI Patterns Used

| Pattern | Implementation |
|---------|---------------|
| Debounced search | `useDebounce(query, 300)` hook |
| Tag input | Enter/comma to add, X to remove, max 10 |
| Status badges | Color-coded: draft (outline), published (green), archived (gray) |
| Copy feedback | 2-second "Copied!" state with checkmark |
| Form validation | Zod schema with react-hook-form |

### Debounce Hook Pattern

```typescript
function useDebounce<T>(value: T, delay: number): T {
    const [debouncedValue, setDebouncedValue] = useState<T>(value)

    useEffect(() => {
        const handler = setTimeout(() => setDebouncedValue(value), delay)
        return () => clearTimeout(handler)
    }, [value, delay])

    return debouncedValue
}

// Usage
const debouncedQuery = useDebounce(query, 300)
useEffect(() => { search(debouncedQuery) }, [debouncedQuery])
```

### Tag Input Pattern

```typescript
function handleAddTag(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" || e.key === ",") {
        e.preventDefault()
        const tag = tagInput.trim().toLowerCase()
        if (tag && !tags.includes(tag) && tags.length < 10) {
            setTags([...tags, tag])
            setTagInput("")
        }
    }
}
```

### Prevention Checklist

- [ ] Public routes use slug, admin routes use ID
- [ ] Search has debounce (300ms typical)
- [ ] Copy button has visual feedback (2s timeout)
- [ ] Status transitions enforced (draft→publish, any→archive)
- [ ] Tag input has max limit and deduplication

---

## Lesson 42: TipTap Content Rendering Pipeline - Separating Special Nodes

**Date**: 2026-01-19
**Context**: SSR rendering of TipTap JSON with code blocks and images required special handling

### Problem

Using `generateHTML()` from `@tiptap/html` works for standard content but produces suboptimal output for:
- Code blocks: No syntax highlighting, no copy button, no line numbers
- Images with placement metadata: No placement-specific styling, no React component features

`dangerouslySetInnerHTML` doesn't allow React components inside the rendered content.

### Solution: Split Rendering Pipeline

Create a `TipTapContentRenderer` that:
1. Iterates through TipTap JSON nodes
2. Accumulates standard nodes for `generateHTML()`
3. Extracts special nodes (code blocks, images) as separate React components
4. Renders interleaved HTML and React components

### Implementation Pattern

```typescript
interface ContentPart {
    type: "html" | "code" | "image"
    content: string
    codeBlock?: CodeBlockData
    imageBlock?: ImageBlockData
}

function TipTapContentRenderer({ content }: { content: any }) {
    const parts = useMemo(() => {
        const result: ContentPart[] = []
        let htmlNodes: any[] = []

        const flushHtmlNodes = () => {
            if (htmlNodes.length > 0) {
                const html = generateHTML({ type: "doc", content: htmlNodes }, extensions)
                result.push({ type: "html", content: html })
                htmlNodes = []
            }
        }

        for (const node of content.content) {
            if (node.type === "codeBlockCustom") {
                flushHtmlNodes()
                result.push({ type: "code", codeBlock: extractCodeData(node) })
            } else if (node.type === "imagePlacement") {
                flushHtmlNodes()
                result.push({ type: "image", imageBlock: extractImageData(node) })
            } else {
                htmlNodes.push(node)
            }
        }
        flushHtmlNodes()
        return result
    }, [content])

    return (
        <div>
            {parts.map((part, i) => {
                if (part.type === "html") {
                    return <div key={i} dangerouslySetInnerHTML={{ __html: part.content }} />
                }
                if (part.type === "code") {
                    return <CodeBlockRenderer key={i} {...part.codeBlock} />
                }
                if (part.type === "image") {
                    return <ImageRenderer key={i} {...part.imageBlock} />
                }
            })}
        </div>
    )
}
```

### Key Benefits

| Benefit | Result |
|---------|--------|
| React components for special blocks | Copy buttons, analytics, interactive features |
| Prism.js syntax highlighting | Client-side, language-aware highlighting |
| Placement-specific image styling | Different layouts for teaser/header/explainer/gallery |
| Proper SSR | Content visible before hydration |

### Prevention Checklist

- [ ] Use `useMemo` for parsing to avoid re-parsing on every render
- [ ] Disable conflicting extensions in StarterKit (`codeBlock: false`)
- [ ] Flush accumulated HTML nodes before AND after loop
- [ ] Handle missing node.content gracefully

---

## Lesson 43: OpenGraph Metadata Extraction from TipTap JSON

**Date**: 2026-01-19
**Context**: Social sharing requires og:image but images are stored in TipTap JSON

### Problem

OpenGraph meta tags must be set at the page level (`generateMetadata()` in Next.js), but images are embedded in TipTap JSON content blocks stored in the database.

### Solution: Extract OG Image with Priority Logic

Create a helper function that traverses TipTap JSON to find the best image for social sharing.

### Priority Order

1. **Teaser** images (explicitly marked for social previews)
2. **Header** images (prominent, full-width)
3. **Any image** (fallback)

### Implementation

```typescript
export function extractOgImage(content: any): {
    src: string
    alt: string
    width?: number
    height?: number
} | null {
    if (!content || content.type !== "doc" || !content.content) {
        return null
    }

    // Priority 1: Teaser images
    for (const node of content.content) {
        if (node.type === "imagePlacement" && node.attrs?.placement === "teaser") {
            return { src: node.attrs.src, alt: node.attrs.alt || "", ... }
        }
    }

    // Priority 2: Header images
    for (const node of content.content) {
        if (node.type === "imagePlacement" && node.attrs?.placement === "header") {
            return { src: node.attrs.src, alt: node.attrs.alt || "", ... }
        }
    }

    // Priority 3: Any image
    for (const node of content.content) {
        if (node.type === "imagePlacement" && node.attrs?.src) {
            return { src: node.attrs.src, alt: node.attrs.alt || "", ... }
        }
    }

    return null
}
```

### Usage in generateMetadata

```typescript
export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
    const post = await fetchPost(params.slug)

    // Extract from blocks
    for (const block of post.blocks || []) {
        if (block.block_type === "markdown" && block.data_json?.tiptap) {
            const extracted = extractOgImage(block.data_json.tiptap)
            if (extracted) {
                return {
                    openGraph: {
                        images: [{ url: extracted.src, alt: extracted.alt }]
                    },
                    twitter: {
                        card: "summary_large_image",
                        images: [extracted.src]
                    }
                }
            }
        }
    }
}
```

### Prevention Checklist

- [ ] Default width/height for og:image (1200x630 recommended)
- [ ] Handle missing alt text gracefully (empty string, not undefined)
- [ ] Set twitter:card to "summary_large_image" when image present
- [ ] Parse JSON if data_json is a string

---

## Lesson 44: E2E Test Patterns for Feature Workflows

**Date**: 2026-01-19
**Context**: Testing collaboration, analytics, distribution, and other feature workflows

### Test Organization Pattern

```
tests/
├── collaboration/
│   └── review-workflow.spec.ts     # Review invite, comments, threading
├── analytics-extended.spec.ts       # Scroll depth, time-on-page
├── distribution.spec.ts             # Markdown export, social share
├── recommendations.spec.ts          # Related posts module
├── prompt-library.spec.ts           # CRUD, search, copy
├── code-embed.spec.ts               # Code block insertion, copy
├── image-placement.spec.ts          # Placement types, OG tags
├── security/
│   ├── xss-audit.spec.ts           # XSS prevention tests
│   └── token-security.spec.ts      # Token validation tests
└── quality-gates.spec.ts            # Performance, a11y, SEO
```

### Cross-Test State Sharing Pattern

For workflows that span multiple tests (e.g., create invite → use invite):

```typescript
test.describe('Review Workflow', () => {
    // Shared state across tests
    let reviewUrl: string | null = null

    test('Admin creates review invite', async ({ page }) => {
        // ... create invite
        reviewUrl = await urlInput.inputValue()  // Store for later tests
    })

    test('Collaborator accesses via token', async ({ page }) => {
        test.skip(!reviewUrl, 'Requires URL from previous test')
        await page.goto(reviewUrl!)
        // ... assertions
    })
})
```

### Graceful Skip Pattern

When features may not exist or data may not be available:

```typescript
test('Related posts appear on content page', async ({ page }) => {
    const articleLink = page.locator('a[href^="/p/"]').first()
    if (await articleLink.count() === 0) {
        test.skip()
        return
    }
    // ... rest of test
})
```

### Request Interception for Analytics

```typescript
test('Copy sends analytics event', async ({ page }) => {
    let analyticsEvent: any = null
    await page.route('**/a/event', async (route) => {
        const data = route.request().postDataJSON()
        if (data?.event_type === 'code_copied') {
            analyticsEvent = data
        }
        await route.continue()
    })

    // Perform action
    await copyButton.click()
    await page.waitForTimeout(1000)

    // Analytics event may have been sent
})
```

### Prevention Checklist

- [ ] Use `test.skip()` for optional features, not `test.fail()`
- [ ] Grant clipboard permissions for copy tests: `context.grantPermissions(['clipboard-read', 'clipboard-write'])`
- [ ] Use `page.waitForLoadState('networkidle')` for API-dependent assertions
- [ ] Filter benign console errors (favicon, 404) in error collection tests

---

## Lesson 45: Security Audit Test Patterns

**Date**: 2026-01-19
**Context**: Automated security testing for XSS, CSRF, and token security

### XSS Payload Test Pattern

```typescript
const xssPayloads = [
    '<script>alert("xss")</script>',
    '<img src=x onerror=alert("xss")>',
    '"><script>alert("xss")</script>',
    "javascript:alert('xss')",
    '<svg onload=alert("xss")>',
]

test('Search input sanitizes script tags', async ({ page }) => {
    await page.goto('/search')
    await searchInput.fill(xssPayloads[0])

    const pageContent = await page.content()
    expect(pageContent).not.toContain('<script>alert')
})
```

### Cookie Security Assertions

```typescript
test('Session cookies have security flags', async ({ page }) => {
    await loginAsAdmin(page)

    const cookies = await page.context().cookies()
    const sessionCookie = cookies.find(c => c.name.includes('session'))

    if (sessionCookie) {
        expect(sessionCookie.httpOnly).toBe(true)
        expect(sessionCookie.sameSite).toMatch(/Strict|Lax/)
        // secure flag only in HTTPS
    }
})
```

### Token Security Tests

```typescript
test('Invalid token returns 401', async ({ page }) => {
    await page.goto('/review/invalid-token-12345')
    await expect(page.getByText(/invalid|expired/i)).toBeVisible()
})

test('Malformed tokens are rejected safely', async ({ page }) => {
    const malformedTokens = [
        '../../../etc/passwd',
        '<script>alert(1)</script>',
        "'; DROP TABLE users; --",
    ]

    for (const token of malformedTokens) {
        await page.goto(`/review/${encodeURIComponent(token)}`)
        await page.waitForLoadState('networkidle')
        // Should not crash
    }
})
```

### API Token Exposure Check

```typescript
test('API tokens not exposed in client code', async ({ page }) => {
    await page.goto('/')
    const pageSource = await page.content()

    expect(pageSource).not.toMatch(/api[_-]?key\s*[:=]\s*["'][a-zA-Z0-9]{20,}["']/i)
    expect(pageSource).not.toMatch(/bearer\s+[a-zA-Z0-9._-]{20,}/i)
})
```

### Prevention Checklist

- [ ] Test all user input vectors (search, forms, URL params, slugs)
- [ ] Verify HttpOnly, Secure, SameSite on session cookies
- [ ] Check for API keys in page source
- [ ] Test path traversal in dynamic routes
- [ ] Verify CSRF token presence in state-changing forms

---

## Lesson 46: Placement-Specific CSS Architecture

**Date**: 2026-01-19
**Context**: Different image placements need different visual treatments

### Problem

Images can have different semantic purposes (teaser for social, header as hero, explainer inline, gallery in grid). Each needs distinct styling but must remain maintainable.

### Solution: BEM-like Placement Classes

Use a consistent naming convention: `.img-{placement}`

```css
/* Base styles for all image placements */
.image-placement {
    display: block;
}

.image-placement img {
    display: block;
}

.image-placement figcaption {
    margin-top: 0.5rem;
    font-size: 0.875rem;
    color: var(--muted-foreground);
}

/* Teaser: Centered, prominent, for social previews */
.img-teaser {
    margin: 2rem auto;
    max-width: 42rem;
}

.img-teaser img {
    width: 100%;
    border: 1px solid var(--border);
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    border-radius: 0.5rem;
}

/* Header: Full-width hero image */
.img-header {
    margin: 2rem -1rem;
}

@media (min-width: 640px) {
    .img-header {
        margin-left: -1.5rem;
        margin-right: -1.5rem;
    }
}

.img-header img {
    width: 100%;
    max-height: 500px;
    object-fit: cover;
}

/* Explainer: Inline, smaller */
.img-explainer {
    margin: 1.5rem auto;
    max-width: 32rem;
}

/* Gallery: Grid-ready */
.img-gallery {
    margin: 1rem 0;
}

.img-gallery img {
    aspect-ratio: 16/9;
    object-fit: cover;
}
```

### React Component Integration

```typescript
function ImageRenderer({ placement, ...props }: ImageRendererProps) {
    return (
        <figure
            className={cn(
                "image-placement not-prose",
                `img-${placement}`
            )}
            data-placement={placement}
        >
            <img {...props} />
            {props.caption && <figcaption>{props.caption}</figcaption>}
        </figure>
    )
}
```

### Responsive Breakout Pattern

For header images that should extend beyond the content column:

```css
.img-header {
    margin-left: -1rem;
    margin-right: -1rem;
}

@media (min-width: 640px) {
    .img-header {
        margin-left: -1.5rem;
        margin-right: -1.5rem;
    }
}

@media (min-width: 768px) {
    .img-header {
        margin-left: -2rem;
        margin-right: -2rem;
    }
}
```

### Prevention Checklist

- [ ] Use `not-prose` to opt out of Tailwind Typography styling
- [ ] Set `object-fit: cover` for images with fixed aspect ratios
- [ ] Use CSS custom properties for colors to support dark mode
- [ ] Add `data-placement` attribute for debugging/analytics
- [ ] Test all placements at mobile, tablet, and desktop breakpoints

---

## Lesson 47: Test Doubles Must Match Production Adapter Signatures

**Date**: 2026-01-19
**Context**: Compliance remediation after rapid feature development

### Problem

During rapid P1 feature development, production adapters evolved to require additional parameters (e.g., `time_port`, `id_provider`, `uuid_provider`) for deterministic testing. However, test doubles (in-memory implementations) were not updated to match, causing test failures:

```python
# Production adapter evolved to:
class InMemoryAggregateRepo:
    def __init__(self, time_port: TimePort, id_provider: IDProvider):
        ...

# But test still used old signature:
repo = InMemoryAggregateRepo()  # TypeError: missing required arguments
```

### Solution

When updating production adapter signatures, always update corresponding test doubles in the same commit:

```python
# test_analytics_aggregate.py
class MockTimePort:
    def __init__(self, fixed_time: datetime | None = None) -> None:
        self._now = fixed_time or datetime(2024, 6, 15, 12, 0, 0, tzinfo=UTC)

    def now_utc(self) -> datetime:
        return self._now

class MockIDProvider:
    def __init__(self) -> None:
        self._counter = 0

    def generate(self) -> UUID:
        self._counter += 1
        return UUID(f"00000000-0000-0000-0000-{self._counter:012d}")

@pytest.fixture
def repo(time_port: MockTimePort, id_provider: MockIDProvider) -> InMemoryAggregateRepo:
    return InMemoryAggregateRepo(time_port=time_port, id_provider=id_provider)
```

### Prevention Checklist

- [ ] When adding parameters to adapter `__init__`, grep for all test instantiations
- [ ] Create shared mock providers in `conftest.py` for reuse across tests
- [ ] Run full test suite before committing adapter changes
- [ ] Add quality gate for provider injection patterns

---

## Lesson 48: Integration Test Database Schemas Must Be Complete

**Date**: 2026-01-19
**Context**: Integration test failures after adding new features

### Problem

Integration tests that create their own test database schemas (without using migrations) become stale when new tables are added. The test continues using a minimal schema while production code expects additional tables:

```python
# Test created only basic tables:
conn.execute("CREATE TABLE content_items (...)")
conn.execute("CREATE TABLE content_blocks (...)")

# But delete operation tried to clean up related tables:
conn.execute("DELETE FROM publish_jobs WHERE content_id = ?")
# sqlite3.OperationalError: no such table: publish_jobs
```

### Solution

Either (1) use actual migrations or (2) keep test schemas in sync with migrations:

```python
# Option 1: Use migrations (preferred)
@pytest.fixture
def setup_db(test_db_path):
    conn = sqlite3.connect(test_db_path)
    with open("migrations/001_initial.sql") as f:
        schema = f.read().split("-- Down")[0]
        conn.executescript(schema)
    conn.close()

# Option 2: Maintain complete inline schema
conn.execute("""
    CREATE TABLE publish_jobs (
        id TEXT PRIMARY KEY,
        content_id TEXT NOT NULL,
        publish_at_utc DATETIME NOT NULL,
        status TEXT NOT NULL,
        ...
    )
""")
```

### Prevention Checklist

- [ ] Prefer using actual migration files in integration tests
- [ ] When adding new tables, search for `CREATE TABLE` in test files
- [ ] Add migration-based test fixtures to shared `conftest.py`
- [ ] Document test database setup requirements in test file headers

---

## Lesson 49: Mock Patch Paths Must Match Post-Refactor Module Locations

**Date**: 2026-01-19
**Context**: Tests failing after directory restructuring

### Problem

After refactoring directory structure (e.g., `src/api/` → `src/app_shell/api/`), mock patch paths become stale:

```python
# Test used old path:
with patch("src.api.routes.public_sharing.run_get") as mock:
    ...
# AttributeError: module 'src' has no attribute 'api'

# Correct path after refactor:
with patch("src.app_shell.api.routes.public_sharing.run_get") as mock:
    ...
```

### Solution

Use `replace_all` when updating module paths, and add a comment noting the full module path:

```python
# Full module path: src.app_shell.api.routes.public_sharing
with patch("src.app_shell.api.routes.public_sharing.run_get") as mock_get_content:
    ...
```

### Prevention Checklist

- [ ] After directory refactoring, grep for old module paths in test files
- [ ] Use IDE "Find and Replace" with regex for bulk updates
- [ ] Run tests immediately after refactoring to catch stale paths
- [ ] Consider using `from module import func` + `patch.object()` for more resilient patching

---

## Lesson 50: Use Specific Exception Types in pytest.raises

**Date**: 2026-01-19
**Context**: Ruff B017 violation during compliance remediation

### Problem

Using `pytest.raises(Exception)` is flagged by ruff B017 as too broad:

```python
# BAD - catches any exception, may mask bugs
with pytest.raises(Exception):  # B017: Do not assert blind exception
    load_rules_file(invalid_path)
```

### Solution

Use the specific exception type expected:

```python
# GOOD - catches only the expected exception
import yaml

with pytest.raises(yaml.YAMLError):
    load_rules_file(invalid_path)
```

### Common Mappings

| Operation | Expected Exception |
|-----------|-------------------|
| YAML parsing | `yaml.YAMLError` |
| JSON parsing | `json.JSONDecodeError` |
| File not found | `FileNotFoundError` |
| Pydantic validation | `pydantic.ValidationError` |
| Key lookup | `KeyError` |
| Type conversion | `ValueError` or `TypeError` |

### Prevention Checklist

- [ ] Always specify the expected exception type
- [ ] If multiple exceptions possible, use `pytest.raises((ExcA, ExcB))`
- [ ] Add comment explaining why this exception is expected
- [ ] Run `ruff check --select B017` to find violations

---

## Lesson 51: Quality Gates Should Exclude Unimplemented Feature Tests

**Date**: 2026-01-19
**Context**: Quality gates failing on tests for future features

### Problem

Tests written for planned-but-not-implemented features (e.g., v4 rules schema) cause quality gate failures even though core functionality is working:

```bash
# Quality gates fail due to tests for v4 rules (not yet implemented)
FAILED tests/unit/test_v4_rules_loader.py::test_load_actual_v4_rules_file
FAILED tests/unit/test_v4_rules_constraints.py::TestR1NoPII::test_analytics_store_ip_is_false
```

### Solution

Configure quality gates to exclude future feature tests:

```python
# scripts/run_quality_gates.py
COMMANDS = {
    "tests": [
        "python3", "-m", "pytest", "-q",
        # Exclude tests for not-yet-implemented features
        "--ignore=tests/unit/test_v4_rules.py",
        "--ignore=tests/unit/test_v4_rules_loader.py",
        "--ignore=tests/unit/test_v4_rules_constraints.py",
        "--json-report",
        f"--json-report-file={ARTIFACTS_DIR / 'pytest-report.json'}",
    ],
}
```

### Alternative: Skip Markers

```python
@pytest.mark.skip(reason="T-0004/T-0005: v4 rules schema to be implemented")
class TestV4RulesLoader:
    ...
```

### Prevention Checklist

- [ ] Use `pytest.mark.skip` with reason for planned tests
- [ ] Document excluded tests in quality gates configuration
- [ ] Review excluded tests during milestone planning
- [ ] Remove exclusions when features are implemented

---

## Lesson 52: Configuration Paths Must Be Consistent Across Codebase

**Date**: 2026-01-19
**Context**: Backup/restore test failing due to directory name mismatch

### Problem

Test created files in one directory, but configuration specified a different directory:

```python
# Test created:
fs_path = tmp_path / "filestore"
(fs_path / "test_asset.txt").write_text("dummy asset")

# But rules.yaml specified:
ops:
  backups:
    include:
      - "lrl.db"
      - "assets"  # Not "filestore"!

# Result: Backup didn't include the test file, restore test failed
```

### Solution

Always reference configuration for path names:

```python
# Read from rules.yaml or use constants
ASSETS_DIR = "assets"  # Matches rules.yaml ops.backups.include

# In test:
assets_path = tmp_path / ASSETS_DIR
assets_path.mkdir()
(assets_path / "test_asset.txt").write_text("dummy asset")
```

### Prevention Checklist

- [ ] Define path constants that match rules.yaml
- [ ] In tests, read actual configuration or use shared constants
- [ ] Add integration test that verifies backup/restore paths match config
- [ ] Document required directory names in README or configuration docs

---

## Lesson 53: E2E Test Selectors Must Match Actual DOM Attributes

**Date**: 2026-01-19
**Context**: Playwright E2E tests timing out on login form

### Problem

Tests written assuming form elements use `name` attributes, but actual implementation uses `data-testid`:

```typescript
// Tests assumed (WRONG):
await page.fill('input[name="email"]', 'admin@example.com');
await page.fill('input[name="password"]', 'password');
await page.click('button[type="submit"]');

// Actual form implementation:
<Input data-testid="login-email" ... />
<Input data-testid="login-password" ... />
<Button data-testid="login-submit" ... />
```

Result: Tests timeout waiting for selectors that don't exist.

### Solution

1. **Read the actual component** before writing tests:
```bash
grep -n "data-testid\|name=" components/auth/login-form.tsx
```

2. **Use Playwright's recommended getByTestId**:
```typescript
await page.getByTestId('login-email').fill('admin@example.com');
await page.getByTestId('login-password').fill('password');
await page.getByTestId('login-submit').click();
```

3. **Batch update with Python** when patterns change across many files:
```python
import re, glob
replacements = [
    (r"page\.fill\('input\[name=\"email\"\]', '([^']+)'\)",
     r"page.getByTestId('login-email').fill('\1')"),
]
for filepath in glob.glob('**/*.spec.ts', recursive=True):
    with open(filepath, 'r') as f:
        content = f.read()
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    with open(filepath, 'w') as f:
        f.write(content)
```

### Prevention Checklist

- [ ] Read component source before writing E2E tests
- [ ] Use `data-testid` attributes consistently in components
- [ ] Prefer `getByTestId()` over CSS selectors for stability
- [ ] Create auth helpers (`loginAsAdmin`, `loginAsEditor`) for reuse
- [ ] Run tests immediately after component changes

---

## Lesson 54: Test Database Seed Scripts Must Match Actual Schema

**Date**: 2026-01-19
**Context**: Seed script failing with "table has no column named X"

### Problem

Seed script assumed a schema that didn't match the actual migrations:

```python
# Seed script assumed:
INSERT INTO users (id, email, name, role, password_hash, ...)
#                       ^^^^  ^^^^
# Actual schema (from 001_initial.sql):
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,  # Not "name"
    password_hash TEXT NOT NULL,
    status TEXT NOT NULL,        # No "role" column
    ...
);
# Roles are in separate table: role_assignments
```

### Solution

1. **Read migration files** before writing seed scripts:
```bash
cat migrations/001_initial.sql | grep -A 10 "CREATE TABLE users"
```

2. **Match schema exactly**:
```python
# CORRECT - matches actual schema
conn.execute("""
    INSERT INTO users (id, email, display_name, password_hash, status, ...)
    VALUES (?, ?, ?, ?, 'active', ...)
""", (admin_id, "admin@example.com", "Test Admin", hashed_pw, ...))

# Add role in separate table
conn.execute("""
    INSERT INTO role_assignments (id, user_id, role, created_at)
    VALUES (?, ?, ?, ?)
""", (uuid4(), admin_id, "admin", now))
```

3. **Remove non-existent columns**:
```python
# BAD - content_blocks doesn't have created_at/updated_at
INSERT INTO content_blocks (..., created_at, updated_at)

# GOOD - only columns that exist
INSERT INTO content_blocks (id, content_item_id, block_type, data_json, position)
```

### Prevention Checklist

- [ ] Read migration SQL before writing seed scripts
- [ ] Use `sqlite3 .schema tablename` to verify columns
- [ ] Run seed script immediately after writing to catch errors
- [ ] Document schema assumptions in seed script docstrings

---

## Lesson 55: Check Port Conflicts Before Starting Local Servers

**Date**: 2026-01-19
**Context**: Next.js failing to start with EADDRINUSE on multiple ports

### Problem

Common development ports (3000, 3001, 3002) may be used by other services:

```bash
# Port 3000 occupied by Docker/Grafana
curl http://localhost:3000/  # Returns Grafana HTML, not Next.js!

# Next.js fails to start
Error: listen EADDRINUSE: address already in use :::3000
Error: listen EADDRINUSE: address already in use :::3001
```

### Solution

1. **Check ports before starting**:
```bash
lsof -i :3000,:3001,:3002 | head -10
netstat -an | grep -E '300[0-9].*LISTEN'
```

2. **Kill conflicting processes**:
```bash
lsof -i :3000 | awk 'NR>1 {print $2}' | xargs kill -9
```

3. **Use non-standard port for development**:
```bash
PORT=4200 npm run start
```

4. **Update Playwright config to match**:
```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    baseURL: 'http://localhost:4200',
  },
  webServer: {
    command: 'PORT=4200 npm run start',
    url: 'http://localhost:4200',
  },
});
```

### Common Port Conflicts

| Port | Common Users |
|------|--------------|
| 3000 | Grafana, Rails, Create-React-App |
| 3001 | BrowserSync, dev servers |
| 5000 | Flask, Airplay Receiver (macOS) |
| 8000 | Django, FastAPI |
| 8080 | Jenkins, many web servers |

### Prevention Checklist

- [ ] Use `lsof -i :PORT` before starting servers
- [ ] Configure non-standard ports in dev environment
- [ ] Document required ports in README
- [ ] Add port conflict check to npm scripts

---

## Lesson 56: Playwright Config Must Match Running Server Ports

**Date**: 2026-01-19
**Context**: Playwright tests hitting wrong server

### Problem

Playwright config specified port 3000, but frontend running on port 4200:

```typescript
// playwright.config.ts (WRONG)
use: {
    baseURL: 'http://localhost:3000',  // Grafana!
},
webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
},

// Actual frontend on port 4200
```

Tests hit Grafana instead of the Next.js app, causing immediate failures.

### Solution

Keep Playwright config synchronized with actual server configuration:

```typescript
// playwright.config.ts (CORRECT)
export default defineConfig({
  use: {
    baseURL: 'http://localhost:4200',
    trace: 'on-first-retry',
  },
  webServer: {
    command: 'PORT=4200 npm run start',
    url: 'http://localhost:4200',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
```

### Environment Variable Approach

```typescript
// playwright.config.ts
const PORT = process.env.FRONTEND_PORT || '4200';

export default defineConfig({
  use: {
    baseURL: `http://localhost:${PORT}`,
  },
  webServer: {
    command: `PORT=${PORT} npm run start`,
    url: `http://localhost:${PORT}`,
  },
});
```

### Prevention Checklist

- [ ] Use environment variables for ports
- [ ] Verify baseURL matches running server with `curl`
- [ ] Set `reuseExistingServer: true` for faster local dev
- [ ] Add port verification step in CI pipeline

---

## Lesson 57: E2E Tests Need Authentication Helpers for Reuse

**Date**: 2026-01-19
**Context**: 16 test files with duplicate login code

### Problem

Login logic duplicated across many test files, making updates painful:

```typescript
// Every test file had:
await page.goto('/login');
await page.fill('input[name="email"]', 'admin@example.com');
await page.fill('input[name="password"]', 'password');
await page.click('button[type="submit"]');
await page.waitForURL(/\/admin/);
```

When selectors changed, 16 files needed updating.

### Solution

Create shared authentication fixtures:

```typescript
// tests/fixtures/auth.ts
import { Page } from '@playwright/test';

export const TEST_ADMIN = {
    email: 'admin@example.com',
    password: 'testpassword123',
};

export const TEST_EDITOR = {
    email: 'editor@example.com',
    password: 'testpassword123',
};

export async function loginAsAdmin(page: Page): Promise<void> {
    await page.goto('/login');
    await page.getByTestId('login-email').fill(TEST_ADMIN.email);
    await page.getByTestId('login-password').fill(TEST_ADMIN.password);
    await page.getByTestId('login-submit').click();
    await page.waitForURL(/\/admin/, { timeout: 10000 });
}

export async function loginAsEditor(page: Page): Promise<void> {
    await page.goto('/login');
    await page.getByTestId('login-email').fill(TEST_EDITOR.email);
    await page.getByTestId('login-password').fill(TEST_EDITOR.password);
    await page.getByTestId('login-submit').click();
    await page.waitForURL(/\/admin/, { timeout: 10000 });
}

export async function logout(page: Page): Promise<void> {
    await page.getByTestId('user-menu').click();
    await page.getByTestId('logout-button').click();
    await page.waitForURL(/\/login/, { timeout: 5000 });
}
```

Usage in tests:

```typescript
import { loginAsAdmin, TEST_ADMIN } from './fixtures/auth';

test.describe('Admin Features', () => {
    test.beforeEach(async ({ page }) => {
        await loginAsAdmin(page);
    });

    test('Can access dashboard', async ({ page }) => {
        await expect(page).toHaveURL(/\/admin/);
    });
});
```

### Seed Data Fixtures

Pair auth helpers with seed data constants:

```typescript
// tests/fixtures/seed-data.ts
export const CONTENT = {
    publishedPost: {
        slug: 'test-published-post',
        title: 'Test Published Post',
    },
    draftPost: {
        slug: 'test-draft-post',
        title: 'Test Draft Post',
    },
};

export const PROMPTS = {
    published: {
        slug: 'test-published-prompt',
        title: 'Test Published Prompt',
    },
};
```

### Prevention Checklist

- [ ] Create `tests/fixtures/auth.ts` with login helpers
- [ ] Create `tests/fixtures/seed-data.ts` with test constants
- [ ] Use `test.beforeEach()` for common login flow
- [ ] Keep credentials in one place (not scattered in tests)
- [ ] Document test user roles and permissions

---

## Lesson 58: Pydantic Literal Types Must Be Consistent Across All Schema Files

**Date**: 2026-01-19
**Context**: Backend API returning 500 errors for content with "tiptap" block type

### Problem

Pydantic `Literal` types were defined in multiple locations with different values:

```python
# src/domain/entities.py
BlockType = Literal["markdown", "image", "chart", "embed", "divider", "tiptap"]
ContentType = Literal["post", "page", "resource_pdf", "prompt"]

# src/app_shell/api/schemas.py (MISSING tiptap and prompt!)
BlockType = Literal["markdown", "image", "chart", "embed", "divider"]
ContentType = Literal["post", "page", "resource_pdf"]
```

When the database contained content with `block_type="tiptap"`, the domain layer accepted it but FastAPI's response validation (using the API schema) rejected it with:

```
fastapi.exceptions.ResponseValidationError: 1 validation error:
  {'type': 'literal_error', 'loc': ('response', 'blocks', 0, 'block_type'),
   'msg': "Input should be 'markdown', 'image', 'chart', 'embed' or 'divider'",
   'input': 'tiptap'}
```

### Solution

Keep Literal type definitions synchronized across all schema files:

```python
# Option 1: Single source of truth (recommended)
# src/domain/types.py
BlockType = Literal["markdown", "image", "chart", "embed", "divider", "tiptap"]
ContentType = Literal["post", "page", "resource_pdf", "prompt"]

# src/domain/entities.py
from .types import BlockType, ContentType

# src/app_shell/api/schemas.py
from src.domain.types import BlockType, ContentType

# Option 2: Keep in sync manually (error-prone)
# When adding new types, update ALL files that define the Literal
```

### Prevention Checklist

- [ ] Define shared Literal types in a single `types.py` module
- [ ] Import Literal types rather than redefining them
- [ ] When adding new enum values, grep for all usages: `grep -r "Literal.*block_type" src/`
- [ ] Add unit test that validates API schema types match domain types
- [ ] Review API response errors carefully - "literal_error" indicates schema mismatch

**Evidence**: E2E tests failing with 500 errors, backend logs showing ResponseValidationError

---

## Lesson 59: Next.js "use client" Directive Affects All Exports

**Date**: 2026-01-19
**Context**: Server-side error when calling utility function from generateMetadata

### Problem

A utility function `extractOgImage()` was exported from a file marked with `"use client"`:

```typescript
// components/content/images/ImageRenderer.tsx
"use client"  // This affects ALL exports!

export function ImageRenderer({ ... }) { ... }  // Needs client (uses DOM)

export function extractOgImage(content: any) {  // Pure function, no client needs
    // Just iterates over JSON - doesn't need browser APIs
}
```

When `generateMetadata()` (a server function) tried to use `extractOgImage()`:

```typescript
// app/p/[slug]/page.tsx
import { extractOgImage } from "@/components/content/images/ImageRenderer";

export async function generateMetadata({ params }) {
    const extracted = extractOgImage(data.tiptap);  // ERROR!
}
```

Error: `Attempted to call extractOgImage() from the server but extractOgImage is on the client.`

### Solution

Move server-compatible utilities to separate files without `"use client"`:

```typescript
// lib/extractOgImage.ts (NO "use client" directive)
export function extractOgImage(content: any): { src: string; alt: string } | null {
    if (!content || content.type !== "doc") return null;
    // ... pure logic, no browser APIs
}

// app/p/[slug]/page.tsx
import { extractOgImage } from "@/lib/extractOgImage";  // Server-safe import
```

### File Organization Pattern

```
components/
  content/
    images/
      ImageRenderer.tsx    # "use client" - UI component
lib/
  extractOgImage.ts        # No directive - server-safe utility
  extractText.ts           # No directive - server-safe utility
```

### Prevention Checklist

- [ ] Only add `"use client"` when the file needs browser APIs (hooks, DOM, events)
- [ ] Pure utility functions should be in `lib/` without client directive
- [ ] If a client component file has utility exports, split them out
- [ ] Test server components that import utilities by running `npm run build`
- [ ] The error message "from the server but X is on the client" indicates boundary violation

**Evidence**: Article pages showing "Application error: a server-side exception has occurred"

---

## Lesson 60: Realistic Test Data Exposes Type Validation Issues

**Date**: 2026-01-19
**Context**: E2E tests passing with synthetic data but failing with real blog content

### Problem

Tests using minimal synthetic data didn't exercise all code paths:

```python
# Synthetic test data (too simple)
content_blocks = [
    {"block_type": "markdown", "data_json": {"text": "Hello"}}
]
```

Real blog content used TipTap format with `block_type="tiptap"`:

```python
# Real data loaded from blog posts
content_blocks = [
    {"block_type": "tiptap", "data_json": {"tiptap": {"type": "doc", ...}}}
]
```

The type mismatch only surfaced when loading realistic data:
- Synthetic data: 53 tests passing
- Realistic data: Revealed schema inconsistency, fixed to 112 tests passing

### Solution

Create a realistic data loader that mirrors production content structure:

```python
# scripts/load_blog_content.py
def markdown_to_tiptap(markdown: str) -> dict:
    """Convert markdown to TipTap JSON format."""
    # Preserves actual content structure

def load_blog_posts(conn, admin_id, blog_dir):
    for md_file in Path(blog_dir).glob("**/*.md"):
        tiptap_content = markdown_to_tiptap(content)
        conn.execute("""
            INSERT INTO content_blocks (block_type, data_json)
            VALUES (?, ?)
        """, ("tiptap", json.dumps({"tiptap": tiptap_content})))
```

### Test Data Strategy

| Data Type | Purpose | Example |
|-----------|---------|---------|
| Synthetic | Unit tests, fast | `{"text": "Test"}` |
| Fixtures | Integration tests | Pre-defined edge cases |
| Realistic | E2E/acceptance | Actual blog posts |
| Production-like | Load testing | Full content volume |

### Prevention Checklist

- [ ] Maintain a realistic data loader script alongside tests
- [ ] Run E2E tests with realistic data before releases
- [ ] Schema changes must update: domain, API schemas, AND test fixtures
- [ ] Include edge cases: empty content, maximum lengths, special characters
- [ ] Test with content created through UI, not just database inserts

**Evidence**: 59 additional tests passing after loading realistic blog content

---

## Lesson 61: E2E Tests Creating Dynamic Content May Fail in Production Mode

**Date**: 2026-01-19
**Context**: Tests creating content via admin UI then viewing publicly

### Problem

E2E tests that followed this pattern often failed:

```typescript
test('Free content is fully accessible', async ({ page }) => {
    // 1. Create content via admin
    await page.goto('/admin/content/new');
    await page.fill('input[name="title"]', title);
    await page.getByTestId('login-submit').click();

    // 2. Publish it
    await page.getByRole('button', { name: 'Publish Now' }).click();

    // 3. View publicly (FAILS!)
    await page.goto(`/p/${slug}`);
    await expect(page.locator('article')).toBeVisible();  // Timeout
});
```

In production mode (`npm run start`), Next.js has:
- Static page caching
- ISR (Incremental Static Regeneration) delays
- Data caching that doesn't immediately reflect new content

### Solution Options

**Option 1: Use existing seed data (recommended for most tests)**

```typescript
import { CONTENT } from './fixtures/seed-data';

test('Free content is fully accessible', async ({ page }) => {
    // Use pre-seeded content
    await page.goto(`/p/${CONTENT.publishedPost.slug}`);
    await expect(page.locator('article')).toBeVisible();
});
```

**Option 2: Force cache revalidation**

```typescript
// After creating content, trigger revalidation
await page.request.post('/api/revalidate', {
    data: { path: `/p/${slug}` }
});
await page.waitForTimeout(1000);  // Allow propagation
await page.goto(`/p/${slug}`);
```

**Option 3: Use dev server for content creation tests**

```typescript
// playwright.config.ts
webServer: {
    command: process.env.TEST_TYPE === 'create'
        ? 'npm run dev'  // Dev mode for content creation tests
        : 'npm run start',  // Prod mode for viewing tests
}
```

### Test Categorization

| Test Type | Server Mode | Data Source |
|-----------|-------------|-------------|
| Viewing existing content | Production | Seed data |
| Creating new content | Development | Dynamic |
| Admin CRUD operations | Development | Dynamic |
| Performance/load tests | Production | Seed data |

### Prevention Checklist

- [ ] Prefer pre-seeded test data for E2E tests
- [ ] Mark tests that create content as "integration" tests
- [ ] Run content-creating tests against dev server
- [ ] Add explicit cache invalidation when testing dynamic content
- [ ] Document expected data state in test fixtures

**Evidence**: Multiple "article not visible" failures for dynamically created content

---

## Lesson 62: Database Tables Must Exist for All Features Being Tested

**Date**: 2026-01-19
**Context**: Backend 500 errors due to missing `redirects` table

### Problem

E2E tests triggered code paths that required database tables not in the test database:

```python
# Error in backend logs
sqlite3.OperationalError: no such table: redirects
```

The test database was created with migrations that didn't include all feature tables:

```sql
-- migrations/001_initial.sql (has users, content_items)
-- migrations/005_redirects.sql (NEVER RUN on test DB!)
```

### Solution

Ensure test database setup runs all migrations:

```python
# scripts/setup_test_db.py
import sqlite3
from pathlib import Path

def setup_test_database(db_path: str):
    conn = sqlite3.connect(db_path)

    # Run ALL migrations in order
    migrations_dir = Path("migrations")
    for migration in sorted(migrations_dir.glob("*.sql")):
        print(f"Running {migration.name}")
        conn.executescript(migration.read_text())

    conn.commit()
    conn.close()
```

Or use a migration runner:

```bash
# In test setup
alembic upgrade head  # SQLAlchemy
python manage.py migrate  # Django
npx prisma migrate deploy  # Prisma
```

### Database Setup Checklist

```bash
#!/bin/bash
# scripts/prepare-test-db.sh

# 1. Remove old test database
rm -f test.db

# 2. Run all migrations
for migration in migrations/*.sql; do
    sqlite3 test.db < "$migration"
done

# 3. Load seed data
python scripts/load_test_data.py

# 4. Verify all tables exist
sqlite3 test.db ".tables" | grep -q "redirects" || echo "WARNING: redirects table missing"
```

### Prevention Checklist

- [ ] Test database setup script runs ALL migrations
- [ ] CI pipeline recreates test DB from scratch
- [ ] Add migration verification step: check expected tables exist
- [ ] Feature flags should disable features, not cause 500 errors
- [ ] Log which migrations have been applied to test database

**Evidence**: `sqlite3.OperationalError: no such table: redirects` in backend logs

---

## Lesson 63: FastAPI Route Ordering - Specific Paths Before Parameters

**Date**: 2026-01-19
**Context**: Admin prompts API returning 404 for `/prompts/tags` endpoint

### Problem

FastAPI matches routes in the order they are defined. A parameterized route like `/prompts/{prompt_id}` will match ANY path starting with `/prompts/`, including literal paths:

```python
# WRONG ORDER - parameterized route catches everything
@router.get("/prompts/{prompt_id}")  # Line 230 - catches "tags", "search", etc.
def get_prompt(prompt_id: str): ...

@router.get("/prompts/tags")  # Line 414 - NEVER REACHED!
def get_all_tags(): ...

@router.get("/prompts/search")  # Line 351 - NEVER REACHED!
def search_prompts(): ...
```

Result: `GET /prompts/tags` returns 404 because it matches `{prompt_id}="tags"` and no prompt with ID "tags" exists.

### Solution

Define specific paths BEFORE parameterized paths:

```python
# CORRECT ORDER - specific paths first
@router.get("/prompts")
def list_prompts(): ...

@router.get("/prompts/tags")  # Specific path - matched first
def get_all_tags(): ...

@router.get("/prompts/search")  # Specific path - matched first
def search_prompts(): ...

@router.get("/prompts/by-tag/{tag}")  # Specific prefix with param
def get_by_tag(tag: str): ...

@router.get("/prompts/{prompt_id}")  # Parameterized - LAST
def get_prompt(prompt_id: str): ...
```

### Prevention Checklist

- [ ] Always define specific paths before parameterized paths
- [ ] Add comment: `# Parameterized routes must come AFTER specific paths`
- [ ] Test all endpoints after adding new routes
- [ ] Consider using route prefixes to avoid conflicts

**Evidence**: `/api/admin/prompts/tags` returning 404 Not Found

---

## Lesson 64: SQLite Threading - check_same_thread for Web Apps

**Date**: 2026-01-19
**Context**: Backend 500 errors with SQLite threading exception

### Problem

SQLite connections are not thread-safe by default. FastAPI handles requests in multiple threads, causing:

```python
sqlite3.ProgrammingError: SQLite objects created in a thread can only be used
in that same thread. The object was created in thread id 6120534016 and this
is thread id 6137360384.
```

This happens when:
1. Connection created at module load time
2. Connection reused across request handlers
3. FastAPI worker threads differ from connection creation thread

### Solution

Add `check_same_thread=False` to all SQLite connections in API routes:

```python
def get_db_connection() -> sqlite3.Connection:
    """Get database connection for API requests."""
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
```

### Files That Need This Fix

Any API route file using `sqlite3.connect()`:
- `admin_prompts.py`
- `admin_analytics_extended.py`
- `admin_collaboration.py`
- `admin_recommendation.py`
- `public.py`
- `analytics_ingest.py`

### Alternative: Connection Per Request

For better isolation, create connections per-request with proper cleanup:

```python
from contextlib import contextmanager

@contextmanager
def get_db():
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()

# Usage in route
def list_items():
    with get_db() as conn:
        cursor = conn.execute("SELECT * FROM items")
        return cursor.fetchall()
```

### Prevention Checklist

- [ ] Always use `check_same_thread=False` for web app SQLite
- [ ] Consider connection pooling for production
- [ ] Test concurrent requests during development
- [ ] Add threading test to CI pipeline

**Evidence**: `sqlite3.ProgrammingError` in backend logs during concurrent requests

---

## Lesson 65: Database Path Consistency Across Route Modules

**Date**: 2026-01-19
**Context**: Prompts created successfully but not appearing in list

### Problem

Different API route modules were using inconsistent database paths:

```python
# admin_prompts.py - WRONG (uses CWD)
_db_path = "lrl.db"

# Other modules - CORRECT (uses LAB_DATA_DIR)
_data_dir = os.environ.get("LAB_DATA_DIR", "./data")
_db_path = f"{_data_dir}/lrl.db"
```

Result: Prompts created via API were saved to `./lrl.db` while the list endpoint read from `./data/lrl.db` - two different databases!

### Solution

Standardize database path configuration across ALL route modules:

```python
# Standard pattern for all route files
import os

# Use same path as rest of app (LAB_DATA_DIR/lrl.db)
_data_dir = os.environ.get("LAB_DATA_DIR", "./data")
_db_path = f"{_data_dir}/lrl.db"

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
```

### Better: Centralized Configuration

```python
# src/app_shell/config.py
import os

class Settings:
    LAB_DATA_DIR = os.environ.get("LAB_DATA_DIR", "./data")
    DB_PATH = f"{LAB_DATA_DIR}/lrl.db"

settings = Settings()

# In route files
from src.app_shell.config import settings

def get_db_connection():
    return sqlite3.connect(settings.DB_PATH, check_same_thread=False)
```

### Prevention Checklist

- [ ] Use centralized settings/config for database path
- [ ] Grep codebase for `sqlite3.connect` to find all connection points
- [ ] Add test that verifies all routes use same database
- [ ] Log database path on startup for debugging

**Evidence**: `POST /api/admin/prompts` returned 201 but `GET /api/admin/prompts` showed empty list

---

## Lesson 66: Parallel Agent Execution Requires Dependency Analysis

**Date**: 2026-01-20
**Context**: User requested "start 4 agents to tackle each phase in parallel"

### Problem

Not all tasks can be parallelized. Phases often have dependencies:

```
Phase 1 (Backend): T-001 → T-002 → T-003 → T-004
Phase 2 (API):     T-005, T-006, T-007 (all depend on Phase 1)
Phase 3 (Frontend): T-011, T-013 (depend on Phase 2)
Phase 4 (Tests):   T-014-016 (depend on ALL above)
```

Starting 4 agents blindly would cause agents to fail or work against incomplete dependencies.

### Solution

Analyze the dependency graph BEFORE launching agents:

```
# Dependency Analysis for Content Tags Feature

T-CTL001 → T-CTL002 (validation needs serialization)
         → T-CTL003 (aggregation needs serialization)

T-CTL003 → T-CTL005 (tags API needs get_all_tags)
T-CTL001 → T-CTL006 (filtering needs serialization)
T-CTL004 → T-CTL007 (home API needs reading time)

# Phase 1 tasks with no dependencies - CAN PARALLELIZE:
- T-CTL001 (tag serialization)
- T-CTL004 (reading time service)
- T-CTL008-010 (frontend components)

# Phase 2 - WAIT for Phase 1, then parallelize:
- T-CTL005, T-CTL006, T-CTL007

# Phase 3 - WAIT for Phase 2
# Phase 4 - WAIT for ALL
```

### Execution Pattern

```
Wave 1: Start 3 agents (T-001, T-004, T-008-010)
        Wait for completion

Wave 2: Start 3 agents (T-005, T-006, T-007)
        Wait for completion

Wave 3: Start 2 agents (T-011, T-013)
        Wait for completion

Wave 4: Run integration tests
```

### Prevention Checklist

- [ ] Always read tasklist dependency graph before parallelizing
- [ ] Group tasks into "waves" based on satisfied dependencies
- [ ] Maximum parallelism = number of tasks with NO unmet dependencies
- [ ] Don't promise "4 parallel agents" without checking dependencies

**Evidence**: Successful 3-wave parallel execution for 16-task feature

---

## Lesson 67: Solution Designer → BA → Coding - The Correct Workflow

**Date**: 2026-01-20
**Context**: User corrected me for jumping straight to coding without design phase

### Problem

When asked to implement a feature, the instinct is to immediately start coding:

```
User: "Add content organization by tags"
Wrong:
  → Edit ContentItem entity to add tags field
  → Start writing repository code
  → Realize halfway through that approach is wrong
```

This leads to wasted effort, scope creep, and architectural debt.

### Solution

Follow the agentic workflow lifecycle:

```
┌─────────────────┐
│ Solution        │ Clarify scope, architecture, tradeoffs
│ Designer        │ Produce: solution_design.md, SUMMARY.md
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Business        │ Create BA artifacts: spec, tasklist, rules
│ Analyst         │ Produce: *_spec.md, *_tasklist.md, *_quality_gates.md
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Coding          │ Execute tasks following TDD, hexagonal architecture
│ Agent           │ Produce: code, tests, evidence artifacts
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ QA              │ Verify quality gates, compliance
│ Reviewer        │ Produce: quality_gates_run.json, test_report.json
└─────────────────┘
```

### When to Use Each Agent

| Agent | Trigger | Output |
|-------|---------|--------|
| Solution Designer | New feature request with unclear scope | Architecture decisions, scope boundaries |
| Business Analyst | Approved solution design | Spec, tasklist, quality gates |
| Coding Agent | Approved BA artifacts | Working code with tests |
| QA Reviewer | After code changes | Compliance verification |

### Prevention Checklist

- [ ] Never edit production code without BA artifacts
- [ ] Solution Designer for scope clarification
- [ ] BA creates the "contract" (spec) before coding
- [ ] Coding Agent follows the tasklist, not ad-hoc changes
- [ ] QA verifies against quality gates

**Evidence**: User correction: "the process for creating new functionality is to start with the solution designer and handoff to the business analyst then code"

---

## Lesson 68: The "But What About" Phenomenon - Feature Tree Evolution

**Date**: 2026-01-20
**Context**: Simple tag feature evolved into landing page enhancements, prompts browsing, reading time estimates

### Problem

New features naturally spawn related requirements:

```
Initial: "Organize content by tags"

But what about...
  → Tags on the landing page?
  → New This Week section?
  → Reading time estimates?
  → Browse Prompts link?
  → Content type badges?
  → Prompts public browsing page?

Feature tree expands:

            Tags (T-001 to T-003)
           /    |         \
          /     |          \
     Tags API  Reading   Frontend
    (T-005-7)  Time     Components
               (T-004)   (T-008-12)
                   \       /
                    \     /
                 Homepage Update
                    (T-011)
                        |
                 Prompts Route
                    (T-013)
                        |
                 Integration Tests
                   (T-014-16)
```

### Why Structured Process Helps

The BA process creates a **bounded scope** before coding begins:

1. **Solution Designer** - Says "yes" to Tags, Landing Page, Prompts; "no" to full Collections system
2. **BA** - Creates 16 tasks, not infinite expansion
3. **Evolution Log** - Documents scope changes with EV entries
4. **Quality Gates** - Define "done" before starting

Without process:
- Feature creep during implementation
- Incomplete testing
- Unclear "done" criteria
- Unplanned dependencies

With process:
- Scope locked at BA phase
- Dependencies mapped in tasklist
- Tests defined in quality gates
- "But what about" becomes EV entry for next iteration

### Managing the "But What About"

```yaml
# evolution.md entry pattern
- id: EV-0008
  date: 2026-01-21
  type: scope_addition
  title: "Add full Collections/Topics feature"
  description: "User mentioned wanting hierarchical topic organization"
  impact: medium
  resolution: "Defer to Extension 3, document in backlog"
  status: logged
```

### Prevention Checklist

- [ ] Solution Designer MUST define out-of-scope items
- [ ] BA creates finite tasklist with clear boundaries
- [ ] New ideas → Evolution log, not immediate implementation
- [ ] Each "but what about" needs justification against scope
- [ ] Review feature tree depth before adding tasks

**Evidence**: 5 feature requests in single conversation, bounded to 16 tasks via BA process

---

## Lesson 69: Centralize Artifacts by Type, Not by Session

**Date**: 2026-01-20
**Context**: Blog content scattered across multiple locations

### Problem

During development, artifacts naturally accumulate in different locations:

```
Session 1 creates:
  /Users/naidooone/Developer/claude/blogs/case-study-1/

Session 2 creates:
  /Users/naidooone/Developer/claude/blogs/case-study-2/

But existing blog series lives at:
  /Users/naidooone/Developer/projects/blog_posts/agentic_building/
```

Result: Related content is fragmented, hard to find, and lacks cohesion.

### Solution

Centralize artifacts by TYPE (what they are) rather than by SESSION (when created):

```
# WRONG: Organized by creation context
/claude/blogs/                    # Some blogs here
/projects/blog_posts/             # Other blogs here
/research_lab/docs/               # More docs scattered

# RIGHT: Organized by artifact type
/projects/blog_posts/             # ALL blog content
├── agentic_building/             # Series 1
├── compliance-remediation/       # Case study 1
└── spec-driven-development/      # Case study 2

/claude/prompts/                  # ALL prompts and lessons
├── agents/                       # Agent prompts
├── devlessons.md                 # Lessons
└── system-prompts-v2/            # System prompts
```

### Benefits

| Scattered | Centralized |
|-----------|-------------|
| "Where's that blog post?" | Single location to check |
| Duplicate content risk | Clear ownership |
| Inconsistent formats | Pattern enforcement |
| Lost context | Related content together |

### Centralization Checklist

- [ ] Blog posts → `/projects/blog_posts/`
- [ ] Development lessons → `/claude/prompts/devlessons.md`
- [ ] Agent prompts → `/claude/prompts/agents/`
- [ ] Project specs → `{project}/` root with naming convention
- [ ] Research artifacts → `{project}/research/` or dedicated folder

### When to Consolidate

Consolidate immediately when:
1. Creating content that belongs with existing related content
2. Session ends and temporary locations contain permanent artifacts
3. Multiple sessions have created similar content types in different places

### Prevention Checklist

- [ ] Before creating new folder, check if appropriate location exists
- [ ] Use consistent naming conventions across sessions
- [ ] Document artifact locations in project CLAUDE.md
- [ ] Consolidate at end of major feature work

**Evidence**: Blog content moved from `/claude/blogs/` to `/projects/blog_posts/` to join existing 21-part series

---

## Lesson 70: Multi-Agent Web Research Pipeline Patterns

**Date**: 2026-01-20
**Context**: Building prospect intelligence system for 225 pension funds
**Project**: `/Users/naidooone/Developer/projects/client-intel/`

### Architecture Pattern

```
Orchestrator (batch coordination, checkpoints)
    ↓
Research Agent (parallel search, content fetch)
    ↓
Extraction Agent (LLM structured output)
    ↓
Validation Agent (schema + quality checks)
    ↓
Storage (SQLite cache + checkpoint)
```

### Key Learnings

**1. LLM Output Validation (~3% failure rate)**
- Claude occasionally returns strings instead of lists for array fields
- Mitigation: Pydantic validation + retry with schema hint
- Future: Use Claude's structured output / tool_use mode

**2. API Concurrency Sweet Spot**
- Concurrency > 3 causes connection timeouts
- Optimal: 2-3 parallel requests with 5s retry delay
- Full 225-prospect batch: ~90 minutes at concurrency 3

**3. Checkpoint/Resume is Critical**
- SQLite checkpoint after each prospect
- Track completed vs failed separately
- Enables graceful recovery from API failures
- Saved ~30 minutes on retry scenarios

**4. Search Query Effectiveness**

| High Value | Low Value |
|------------|-----------|
| `"{name}" ACFR` | `"{name}" "drift bands"` |
| `"{name}" "Investment Policy"` | `"{name}" "Aladdin"` |
| `"{name}" CIO` | Technology-specific terms |

**5. Data Quality by Segment**

| Segment | Coverage | Notes |
|---------|----------|-------|
| US Public Pension | High | ACFRs, board minutes public |
| Canadian Pension | High | Strong disclosure requirements |
| Corporate ERISA | Low | Limited public filings |
| Endowments | Medium | 990s available but sparse |

### Cost Model

```
Per prospect:
- Tavily: 10 queries × $0.001 = $0.01
- Claude: 2 calls × $0.003 = $0.006
- Total: ~$0.016/prospect

Full batch (225): ~$30
```

### Reusable Components

1. **Pydantic schema enforcement** - Catch LLM errors early
2. **SQLite checkpoint adapter** - Zero-infra resumability
3. **Rich progress tracking** - Essential for long batches
4. **Query template system** - Configurable search patterns

### Anti-Patterns Avoided

- ❌ In-memory state (lost on crash)
- ❌ High concurrency (API timeouts)
- ❌ Single-pass extraction (no retry on validation fail)
- ❌ Hardcoded queries (inflexible)

### Prevention Checklist

- [ ] Use Pydantic models for all LLM output validation
- [ ] Implement checkpoint/resume for batches > 50 items
- [ ] Keep API concurrency ≤ 3 for stability
- [ ] Cache search results to reduce costs on retry
- [ ] Track success/failure separately in checkpoints

**Evidence**: 225 prospects processed, 97% success rate, $7.4T AUM coverage

---

## Lesson 71: Database Migrations Must Run Automatically on App Startup

**Date**: 2026-01-20
**Project**: Little Research Lab
**Category**: Deployment / Database

### Context

Deploying to Fly.io after adding a `tags_json` column. Production database had no `_migrations` table - migrations had been applied manually or not tracked.

### Problem

Manual migration processes are error-prone and easily forgotten during deployment. Schema drift between environments causes runtime failures that are hard to debug in production.

### Solution

Add automatic migration execution to FastAPI lifespan handler:

```python
from contextlib import asynccontextmanager
from src.adapters.sqlite.migrator import SQLiteMigrator

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    migrations_dir = os.path.join(settings.base_dir, "migrations")
    if os.path.exists(migrations_dir):
        migrator = SQLiteMigrator(settings.db_path, migrations_dir)
        migrator.run_migrations()
        print(f"INFO: Database migrations applied from {migrations_dir}")
    yield
```

### Key Insight

Migrations should be idempotent and self-tracking. SQLiteMigrator maintains a `_migrations` table and only applies migrations not yet recorded.

### Prevention Checklist

- [ ] Always run migrations automatically on app startup
- [ ] Use a migration tracking table (`_migrations`)
- [ ] Make migrations idempotent (safe to run multiple times)
- [ ] Log migration activity for debugging
- [ ] Include migration scripts in Docker images

**Evidence**: Deployment succeeded with automatic schema sync

---

## Lesson 72: Test Schemas Drift from Production Migrations

**Date**: 2026-01-20
**Project**: Little Research Lab
**Category**: Testing / Database

### Context

Integration tests using inline SQL schema definitions failed after adding `tags_json` column via migration.

### Problem

Tests that create their own database schemas inline (rather than using the migration system) drift from production schema over time:

```python
# Bad: Inline schema missing new columns
cursor.execute("""CREATE TABLE content_items (
    id TEXT PRIMARY KEY,
    title TEXT
    -- Missing tags_json column!
)""")
```

### Solution

Two approaches:

**Option 1 (Preferred)**: Use the same migration system in tests:
```python
from src.adapters.sqlite.migrator import SQLiteMigrator

migrator = SQLiteMigrator(db_path, "migrations")
migrator.run_migrations()
```

**Option 2**: When inline schemas are necessary, keep them in sync:
```python
cursor.execute("""CREATE TABLE content_items (
    id TEXT PRIMARY KEY,
    title TEXT,
    tags_json TEXT DEFAULT '[]'  -- Add new columns!
)""")
```

### Key Insight

Tests are a second source of truth for database schema. When they diverge from migrations, you get false positives locally and failures in CI/production.

### Prevention Checklist

- [ ] Prefer using migration system in integration tests
- [ ] If using inline schemas, maintain a single source definition
- [ ] Add test that verifies inline schemas match migration result
- [ ] Review test schemas when adding new migrations

**Evidence**: Two test files fixed: `test_content_routes.py`, `test_collab_flow.py`

---

## Lesson 73: FastAPI 204 Status Endpoints Require response_model=None

**Date**: 2026-01-20
**Project**: Little Research Lab
**Category**: FastAPI / API Design

### Context

Deployment failed with: `AssertionError: Status code 204 must not have a response body`

### Problem

FastAPI validates that 204 No Content responses have no body. If you specify `status_code=status.HTTP_204_NO_CONTENT` without `response_model=None`, FastAPI may still try to serialize a response:

```python
# Bad: Missing response_model=None
@router.delete("/items/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(id: str) -> None:
    ...
```

### Solution

Always pair 204 status codes with explicit `response_model=None`:

```python
# Good: Explicit no response model
@router.delete(
    "/items/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
def delete_item(id: str) -> None:
    ...
```

### Affected Patterns

This applies to:
- DELETE endpoints (most common)
- POST endpoints that return 204 (e.g., cache invalidation)
- Any endpoint where 204 is appropriate

### Prevention Checklist

- [ ] Always add `response_model=None` when using `status_code=204`
- [ ] Search codebase for `HTTP_204` and verify each has `response_model=None`
- [ ] Add integration test that verifies 204 endpoints work

**Evidence**: Fixed 4 endpoints across `admin_collaboration.py` and `admin_recommendation.py`

---

## Lesson 74: Dockerfile Entrypoints Must Match Actual Module Paths

**Date**: 2026-01-20
**Project**: Little Research Lab
**Category**: Docker / Deployment

### Context

Deployment failed with: `ModuleNotFoundError: No module named 'src.api'`

### Problem

After refactoring module structure (e.g., `src/api/` → `src/app_shell/api/`), Dockerfile CMD wasn't updated:

```dockerfile
# Bad: Old module path
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Solution

Update Dockerfile to match actual module path:

```dockerfile
# Good: Matches refactored structure
CMD ["uvicorn", "src.app_shell.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Key Insight

Dockerfiles are often forgotten during refactors because they're not part of the main codebase IDE navigation. Module path changes should trigger a search for references in:
- Dockerfiles
- docker-compose.yml
- CI/CD configs
- Deployment scripts
- Documentation

### Prevention Checklist

- [ ] After module refactors, search for old module names in all config files
- [ ] Add local Docker build test to CI before deploy
- [ ] Consider using a single source of truth for module paths (e.g., environment variable)

**Evidence**: Deployment succeeded after fixing `src.api.main` → `src.app_shell.api.main`

---

## Lesson 75: Include Utility Scripts in Docker Images

**Date**: 2026-01-20
**Project**: Little Research Lab
**Category**: Docker / Operations

### Context

Created `scripts/run_migrations.py` for manual migration runs but forgot to include in Docker image.

### Problem

Utility scripts needed for production operations (manual migrations, data fixes, debugging) aren't available if not explicitly copied to Docker image:

```dockerfile
# Missing scripts directory
COPY src/ src/
COPY rules.yaml .
# scripts/ not copied!
```

### Solution

Include scripts directory in Dockerfile:

```dockerfile
COPY src/ src/
COPY rules.yaml .
COPY seed_db.py .
COPY migrations/ migrations/
COPY scripts/ scripts/  # Don't forget utility scripts!
```

### When You Need Operational Scripts

- **Migration scripts**: Manual schema changes, data migrations
- **Seed scripts**: Populating test data
- **Debug scripts**: Database inspection, log analysis
- **Backup scripts**: Data export utilities

### Prevention Checklist

- [ ] Create `scripts/` directory for operational utilities
- [ ] Always include `scripts/` in Dockerfile COPY
- [ ] Document available scripts in README or DEPLOY.md
- [ ] Test scripts work inside container before deploying

**Evidence**: Added `COPY scripts/ scripts/` to Dockerfile

---

## Lesson 76: Background Subagents Cannot Prompt for Bash Permissions

**Date**: 2026-01-22
**Project**: Little Research Lab
**Category**: Claude Code / Subagent Architecture

### Context

Ran 5 parallel subagents to fix security issues across backend and frontend. Frontend agents completed successfully, but backend agents got stuck in infinite retry loops.

### Problem

Background subagents (`run_in_background: true`) cannot prompt the user for permissions. When they attempt bash commands that require approval (not in the auto-allow list), the command is auto-denied:

```
Permission to use Bash has been auto-denied (prompts unavailable).
```

The agents then retry the same command indefinitely, consuming tokens without progress.

**Commands that triggered this issue:**
```bash
LAB_SECRET_KEY=test-secret pytest  # env var prefix not in allow list
.venv/bin/pytest --tb=short        # venv path not standard
```

**Commands that work in background:**
```bash
pytest                    # Standard command, auto-allowed
npm run build            # Standard command, auto-allowed
npm run lint             # Standard command, auto-allowed
git status               # Standard command, auto-allowed
```

### Root Cause

The `~/.claude/settings.local.json` permissions are evaluated at command execution time. Background agents can't display permission prompts, so any command not explicitly allowed gets denied silently.

### Solution

**Option 1: Tell agents "make changes only, don't verify"**
```
After making changes, DO NOT run tests. Just report what you changed.
```

**Option 2: Don't use background mode for verification tasks**
- Keep agents in foreground when they need to run pytest/verification
- Use background mode only for read/write operations

**Option 3: Pre-approve verification commands**
Add specific patterns to settings.local.json:
```json
{
  "permissions": {
    "allow": [
      "Bash(LAB_SECRET_KEY=*:*)",
      "Bash(pytest:*)"
    ]
  }
}
```

**Option 4: Run verification in parent agent**
```
- Launch subagent for code changes (background)
- Wait for completion
- Run verification myself (parent can prompt)
```

### Pattern: Splitting Code Changes from Verification

```
# GOOD: Parallel code changes, sequential verification
1. Launch N background agents for code changes only
2. Wait for all to complete
3. Run single verification command in parent:
   - pytest (backend)
   - npm run build && npm run lint (frontend)
```

### What Commands Are Auto-Allowed?

Check `~/.claude/settings.local.json` for the allow list. Common safe patterns:
- `pytest`, `npm test`, `bun test`, `ruff`, `mypy`
- `npm run build`, `npm run lint`
- `git status`, `git diff`, `git log`
- `ls`, `cat`, `head`, `tail`, `grep`, `find`

### Prevention Checklist

- [ ] For background agents, only request operations that don't need verification
- [ ] If verification needed, either:
  - Run agent in foreground (no `run_in_background`)
  - Do verification in parent after agent completes
- [ ] Check settings.local.json before assuming commands will work
- [ ] Watch for "Permission auto-denied" in agent output - indicates stuck loop
- [ ] Consider adding common verification patterns to allow list

### Symptoms of Stuck Agent

- Agent keeps running but makes no progress
- Output shows repeated "Permission to use Bash has been auto-denied"
- Token usage climbs without new tool calls succeeding
- Agent doesn't terminate naturally

**Evidence**: Backend agents stuck retrying `LAB_SECRET_KEY=test-secret pytest` 50+ times before manual intervention

---

## Lesson 77: Token Validation Must Use Constant-Time Comparison

**Date**: 2026-01-22
**Project**: Little Research Lab
**Category**: Security

### Problem

Token validation code that looks up tokens by hash and returns early on "not found" creates a timing oracle vulnerability. Attackers can measure response times to guess valid tokens.

```python
# VULNERABLE - early return creates timing oracle
token = self.repository.find_by_hash(token_hash)
if token is None:
    return TokenValidation(result=TokenValidationResult.NOT_FOUND)
```

### Solution

Use `hmac.compare_digest()` for constant-time comparison, even after database lookup:

```python
import hmac

token = self.repository.find_by_hash(token_hash)
if token is None:
    return TokenValidation(result=TokenValidationResult.NOT_FOUND)

# Constant-time comparison - defense in depth
if not hmac.compare_digest(token.token_hash, token_hash):
    return TokenValidation(result=TokenValidationResult.NOT_FOUND)
```

### Why This Matters

- Database lookups can have variable timing based on cache hits, index traversal
- Even microsecond differences are measurable with enough samples
- Password reset tokens are high-value targets
- Defense in depth: add constant-time comparison even when it seems redundant

### Checklist

- [ ] All token validation uses `hmac.compare_digest()`
- [ ] Password reset endpoints have minimum response time (e.g., 200ms)
- [ ] Email enumeration prevented (same response for valid/invalid emails)
- [ ] Rate limiting on auth endpoints

---

## Lesson 78: Environment Variables Should Be Optional for Testing

**Date**: 2026-01-22
**Project**: Little Research Lab
**Category**: Testing, Configuration

### Problem

Hard-coded `RuntimeError` for missing environment variables blocks testing:

```python
# BLOCKS TESTING
SECRET_KEY = os.environ.get("LAB_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("LAB_SECRET_KEY must be set")
```

This causes:
- `ImportError` when running pytest without env var
- CI/CD pipeline failures
- Developer friction

### Solution

Make environment variables optional for non-production:

```python
_env = os.environ.get("ENV", "development")
SECRET_KEY = os.environ.get("LAB_SECRET_KEY")
if not SECRET_KEY:
    if _env == "production":
        raise RuntimeError("LAB_SECRET_KEY must be set in production")
    SECRET_KEY = "dev-only-secret-key-not-for-production"
```

### Best Practices

1. **Production-only enforcement**: Check `ENV=production` before raising
2. **Obvious dev defaults**: Use names like `"dev-only-..."` to prevent accidents
3. **Document requirements**: README should list required env vars for production
4. **CI with real values**: CI pipeline should set env vars to test production path

---

## Lesson 79: Atomic Components Require contract.md Files

**Date**: 2026-01-22
**Project**: Little Research Lab
**Category**: Architecture, Documentation

### Problem

QA review failed because `contract.md` files were missing from components:

```
| Component | contract.md |
|-----------|-------------|
| auth_tokens | ✗ MISSING |
| access_control | ✗ MISSING |
```

Even though components had all code files, missing contracts violated atomic component pattern.

### Required Files for Atomic Components

```
src/components/<name>/
├── __init__.py         # Re-exports
├── component.py        # Core logic
├── models.py           # Data structures
├── ports.py            # Protocol definitions
├── contract.md         # PUBLIC CONTRACT ← Often forgotten
├── errors.py           # Custom exceptions (optional)
└── adapters/           # Implementations (optional)
```

### contract.md Template

```markdown
## COMPONENT_ID
C-<name>

## PURPOSE
One-line description with spec refs.

## INPUTS
- `method(args)`: Description

## OUTPUTS
- `OutputType`: Description

## DEPENDENCIES (PORTS)
- `PortName`: What it does

## SIDE EFFECTS
- What state changes

## INVARIANTS
- I1: Rule that must always hold
- I2: Another invariant

## ERROR CONDITIONS
- `ErrorType`: When it's raised

## TEST REQUIREMENTS
- Coverage target: X%
- Required test scenarios
```

### Checklist

- [ ] Every component has `contract.md`
- [ ] Contract lists all public methods
- [ ] Invariants are testable assertions
- [ ] Error conditions map to exception types

---

## Lesson 80: MyPy Requires Explicit None Checks for Optional Types

**Date**: 2026-01-22
**Project**: Little Research Lab
**Category**: Type Safety, Python

### Problem

MyPy errors when `datetime | None` is passed where `datetime` is expected:

```python
# ERROR: Argument "expires_at" has incompatible type "datetime | None"; expected "datetime"
return AuthToken(
    expires_at=parse_dt(row["expires_at"]),  # parse_dt returns datetime | None
)
```

### Solution

Add explicit assertions before use:

```python
expires_at = parse_dt(row["expires_at"])
created_at = parse_dt(row["created_at"])
assert expires_at is not None, "expires_at is required"
assert created_at is not None, "created_at is required"

return AuthToken(
    expires_at=expires_at,
    created_at=created_at,
)
```

### When to Use Each Pattern

| Pattern | Use When |
|---------|----------|
| `assert x is not None` | Value should never be None (programming error if it is) |
| `if x is None: raise ValueError()` | None is possible user/data error |
| `x = x or default` | None is acceptable, use default |
| `if x is not None:` | None is valid, skip processing |

### Common MyPy Errors and Fixes

```python
# "Item 'None' of 'X | None' has no attribute 'y'"
assert obj is not None
obj.y  # Now safe

# "Argument has incompatible type 'X | None'; expected 'X'"
value = get_optional_value()
assert value is not None
use_required_value(value)  # Now typed as X, not X | None
```

---

## Lesson 81: React setState in useEffect Should Use useMemo for Derived State

**Date**: 2026-01-22
**Project**: Little Research Lab
**Category**: React, Performance

### Problem

React linter error: "Calling setState synchronously within an effect can trigger cascading renders"

```tsx
// BAD - causes cascading renders
const [errors, setErrors] = useState({});

useEffect(() => {
    const newErrors = computeErrors(rules);
    setErrors(newErrors);  // ← Triggers re-render, which triggers effect again
}, [rules]);
```

### Solution

Use `useMemo` for derived state instead of `useState` + `useEffect`:

```tsx
// GOOD - computed value, no cascading renders
const errors = useMemo(() => {
    return computeErrors(rules);
}, [rules]);
```

### When to Use Each Pattern

| Pattern | Use Case |
|---------|----------|
| `useMemo` | Derived/computed values from props/state |
| `useState` + `useEffect` | Async operations, subscriptions, side effects |
| `useRef` + `useEffect` | Tracking previous values, avoiding re-renders |

### Hydration Pattern Exception

For SSR hydration, `setState` in `useEffect` is intentional:

```tsx
useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setMounted(true);  // Intentional for hydration
}, []);
```

Add eslint-disable comment to document the intentional pattern.

---

## Lesson 82: Skipped Test Files Still Need Valid Python Syntax

**Date**: 2026-01-22
**Project**: Little Research Lab
**Category**: Testing, Linting

### Problem

Ruff E402 error in skipped test files:

```python
import pytest
pytestmark = pytest.mark.skip(reason="Not implemented")

from nonexistent.module import Thing  # E402: Module level import not at top of file
```

Even though tests are skipped, ruff still validates import order.

### Solution

Use `TYPE_CHECKING` pattern for imports that may fail:

```python
from __future__ import annotations
from typing import TYPE_CHECKING

import pytest

pytestmark = pytest.mark.skip(reason="Not implemented")

if TYPE_CHECKING:
    from nonexistent.module import Thing
else:
    try:
        from nonexistent.module import Thing
    except ImportError:
        Thing = None  # type: ignore[misc,assignment]
```

### Why This Works

1. `TYPE_CHECKING` imports are only processed by type checkers, not at runtime
2. The `else` branch handles runtime gracefully
3. Ruff sees imports at top level (inside `if TYPE_CHECKING`)
4. No E402 violation because `if TYPE_CHECKING` is valid before other imports

### Alternative: Move Skip to Test Level

```python
from nonexistent.module import Thing  # At top, may fail

@pytest.mark.skip(reason="Not implemented")
def test_something():
    pass
```

This only works if the import succeeds. Use `TYPE_CHECKING` pattern when imports will fail.

---

## Lesson 83: Clarify Data Location Before Debugging "Missing" Content

**Date**: 2026-01-23
**Project**: Little Research Lab
**Category**: Debugging, UX, Content Management

### Problem

User reported "image doesn't render" for a blog post. Investigation consumed significant time checking:
- TipTap extension configuration
- Content save/load flow
- Backend API serialization
- Frontend rendering components

After thorough code review, the actual finding: **no image data existed in the content at all**.

### Root Cause Options

1. Image was never added to the post
2. Image was added but post wasn't saved afterward
3. User expected a "featured image" field that doesn't exist in the schema
4. Confusion about where images should be stored (inline vs. metadata field)

### Solution: Clarify First, Debug Second

Before deep-diving into code, verify the data exists:

```bash
# Check if image nodes exist in content
curl -s "API_URL/api/public/content/SLUG" | jq '.blocks[0].data_json.tiptap.content[] | select(.type == "imagePlacement")'

# List all node types
curl -s "API_URL/api/public/content/SLUG" | jq '.blocks[0].data_json.tiptap.content | map(.type) | unique'
```

### Checklist Before Debugging "Missing Content"

1. **Verify data exists** in the API response
2. **Ask user**: Where was the content added? (editor body, metadata field, separate form?)
3. **Ask user**: Was the item saved after adding the content?
4. **Check schema**: Does the expected field actually exist in the data model?
5. **Then debug code** if data exists but doesn't render

### Key Insight

"It should be there" ≠ "It is there". Always verify data presence before investigating rendering/persistence bugs.

---

## Lesson 84: Database Overrides for YAML-Defined Configuration

**Date**: 2026-01-23
**Project**: Little Research Lab
**Category**: Architecture, Configuration Management

### Problem

Content types are defined in `rules.yaml` but users need to toggle them enabled/disabled at runtime without editing YAML.

### Solution: Override Pattern

Store runtime overrides in database, merge with YAML defaults:

```python
# 1. Load from YAML
yaml_types = load_content_types_from_rules()

# 2. Load overrides from database
overrides = json.loads(site_settings_repo.get("content_type_overrides") or "{}")

# 3. Merge: database overrides win
for type_config in yaml_types:
    if type_config.name in overrides:
        type_config.enabled = overrides[type_config.name]
```

### API Design

```python
# PATCH to toggle individual type
@router.patch("/{type_name}")
def toggle_content_type(type_name: str, request: ContentTypeToggleRequest):
    overrides = json.loads(site_settings_repo.get("content_type_overrides") or "{}")
    overrides[type_name] = request.enabled
    site_settings_repo.set("content_type_overrides", json.dumps(overrides))

# POST to reset all overrides
@router.post("/reload")
def reload_content_types():
    site_settings_repo.set("content_type_overrides", "{}")
    return load_content_types_from_rules()
```

### Benefits

1. YAML remains the source of truth for defaults
2. Runtime changes don't require redeployment
3. "Reset to defaults" clears all overrides
4. Changes persist across restarts

### Frontend Pattern

Use Switch components with optimistic UI updates:

```tsx
const handleToggle = async (name: string, enabled: boolean) => {
    await AdminContentTypesService.toggleContentType(name, { enabled })
    setTypes(prev => prev.map(t => t.name === name ? { ...t, enabled } : t))
}
```

---

## Lesson 85: Next.js Static Generation Timeouts for Demo Pages

**Date**: 2026-01-23
**Project**: Little Research Lab
**Category**: Next.js, Build, Performance

### Problem

Build failed with timeout on demo page:

```
Failed to build /demo/profile/page: /demo/profile (attempt 1 of 3) because it took more than 60 seconds.
Failed to build /demo/profile/page: /demo/profile after 3 attempts.
Export encountered an error on /demo/profile/page: /demo/profile, exiting the build.
```

### Root Cause

Demo pages with complex components (ProfileBioCardDemo) were timing out during static generation because they:
1. Import heavy component trees
2. May trigger client-side code during SSG
3. Have complex initialization logic

### Solution

Skip static generation for demo/preview pages:

```tsx
// frontend/app/demo/profile/page.tsx

// Skip static generation for demo page
export const dynamic = 'force-dynamic';

export default function ProfileDemoPage() {
    return (
        <PublicLayout>
            <ProfileBioCardDemo />
        </PublicLayout>
    );
}
```

### When to Use `force-dynamic`

| Use `force-dynamic` | Keep Static |
|---------------------|-------------|
| Demo/preview pages | Marketing pages |
| Pages with cookies/auth | Blog posts |
| Heavy interactive components | Documentation |
| Admin dashboards | Landing pages |

### Alternative Solutions

1. **Increase timeout** in `next.config.js` (not recommended)
2. **Lazy load** heavy components with `dynamic()`
3. **Split demo component** into lighter preview version
4. **Move to route group** with different rendering strategy

### Build Error Pattern Recognition

```
took more than 60 seconds → Add export const dynamic = 'force-dynamic'
used `cookies` → Add export const dynamic = 'force-dynamic'
used `headers` → Add export const dynamic = 'force-dynamic'
```

---

## Lesson 86: Role-Based Profile Display Requires Correct Role Assignment

**Date**: 2026-01-23
**Project**: Little Research Lab
**Category**: Authorization, Data Access

### Problem

Profile info wasn't displaying on the public About page despite being saved correctly in the admin.

### Root Cause

Backend looked up profile using role filter:

```python
def get_author_profile():
    user = user_repo.get_by_role("owner")  # Returns None!
    return user.profile if user else None
```

The user only had "admin" role in `role_assignments` table, not "owner".

### Solution

Add the required role to the user:

```sql
INSERT INTO role_assignments (id, user_id, role, created_at)
VALUES (gen_uuid(), 'user-uuid', 'owner', datetime('now'));
```

### Debugging Checklist for "Data Not Displaying"

1. **Verify data saved**: Check database directly or via admin API
2. **Check API response**: Does the public endpoint return the data?
3. **Check access control**: Is there role/permission filtering?
4. **Check role assignments**: Does user have required roles?
5. **Check visibility settings**: Is content public?

### Prevention

Document which roles are required for specific features:

```yaml
# In rules.yaml or spec
features:
  author_profile_display:
    requires_role: "owner"
    reason: "Only the site owner's profile displays on public pages"
```

---

## Lesson 87: Prime Directive Compliance Remediation (TimePort, EnvConfigPort)

**Date**: 2026-01-24
**Project**: Little Research Lab
**Category**: Architecture, Hexagonal, Testing, Determinism

### Problem

Compliance audit found 3 types of Prime Directive violations:
1. **14 datetime.utcnow defaults** in domain entities (non-deterministic)
2. **10+ LondonTimeAdapter imports** in components (direct adapter dependency)
3. **1 os import** in domain services (infrastructure leak)

### Root Cause

Original code used convenience shortcuts that violated hexagonal architecture:

```python
# BAD: Domain entity with hardcoded system time
class User(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)

# BAD: Component imports adapter directly
from src.adapters.time_london import LondonTimeAdapter
now = LondonTimeAdapter().now_utc()

# BAD: Domain reads environment directly
import os
rules_path = os.getenv("RULES_PATH", "rules.yaml")
```

### Solution

**1. Entity timestamps**: Remove defaults, make callers pass explicitly

```python
# GOOD: No default - caller must provide
class User(BaseModel):
    created_at: datetime | None = None  # Or required: datetime
```

**2. Component time**: Use TimePort protocol injection

```python
# GOOD: Inject TimePort via constructor
class MyService:
    def __init__(self, time_port: TimePort):
        self._time_port = time_port

    def do_work(self):
        now = self._time_port.now_utc()  # Deterministic in tests
```

**3. Environment access**: Use EnvConfigPort protocol

```python
# GOOD: Create port and adapter
class EnvConfigPort(Protocol):
    def get_env_var(self, name: str, default: str | None = None) -> str | None: ...

class EnvConfigAdapter:
    def get_env_var(self, name: str, default: str | None = None) -> str | None:
        return os.getenv(name, default)
```

### Key Insights

**1. Test Updates Cascade**: Removing entity defaults broke 15+ test files that relied on auto-timestamps. Each needed MockTimePort fixture:

```python
class MockTimePort:
    def __init__(self, fixed: datetime | None = None):
        self._now = fixed or datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC)

    def now_utc(self) -> datetime:
        return self._now
```

**2. Rate Limiter Gotcha**: InMemoryRateLimiter internally uses time, so it needs TimePort:

```python
# FAILS: Rate limiter creates default time source
service = AnalyticsIngestionService(
    event_store=store,
    time_port=time_port,  # Not enough!
)

# WORKS: Explicit rate limiter with TimePort
rate_limiter = InMemoryRateLimiter(time_port=time_port)
service = AnalyticsIngestionService(
    event_store=store,
    rate_limiter=rate_limiter,  # Explicit
    time_port=time_port,
)
```

**3. Foreign Key Constraints**: API tests creating content items failed because `owner_user_id` referenced non-existent users. Fix: create test_user fixture first:

```python
@pytest.fixture
def test_user(user_repo: SQLiteUserRepo) -> User:
    user = User(id=uuid4(), email="test@example.com", ...)
    user_repo.save(user)
    return user

def test_something(content_repo, test_user):
    create_content_item(content_repo, owner_user_id=test_user.id, ...)
```

### Remediation Checklist

When removing Prime Directive violations:

- [ ] **Grep for violations**: `datetime.utcnow`, adapter imports, `os.getenv` in domain
- [ ] **Update entities**: Remove `default_factory=datetime.utcnow`
- [ ] **Update components**: Replace adapter imports with port injection
- [ ] **Create ports**: EnvConfigPort, TimePort, etc.
- [ ] **Update tests**: Add MockTimePort fixtures
- [ ] **Check cascades**: Services that use time internally (rate limiters, caches)
- [ ] **Check FK constraints**: Test fixtures need valid parent records
- [ ] **Run full test suite**: `pytest tests/ -v`

### Prevention Checklist

Add to quality gates:

```bash
# No datetime.utcnow in entities
grep -r "datetime.utcnow" src/domain/entities.py && exit 1

# No adapter imports in components
grep -r "LondonTimeAdapter\|import os" src/components/ && exit 1

# No os import in domain (except ports)
grep -r "^import os" src/domain/ && exit 1
```

### Test File Updates Summary

| File | Changes |
|------|---------|
| `tests/unit/test_settings.py` | MockTimePort fixture |
| `tests/unit/test_analytics_ingest.py` | Rate limiter with TimePort |
| `tests/unit/test_redirects.py` | MockTimePort fixture |
| `tests/unit/test_scheduler.py` | MockTimePort fixture |
| `tests/unit/test_assets.py` | MockTimePort fixture |
| `tests/api/test_admin_*.py` | MockTimePort fixtures |
| `tests/api/test_public_*.py` | test_user + MockTimePort fixtures |

---

---

## Lesson 88: Unity Catalog Volumes Required When DBFS Public Access Disabled

**Date**: 2026-01-24
**Project**: dbxloader (Databricks POC)
**Category**: Databricks, Infrastructure, Cloud Storage

### Problem

Attempted to load CSV files from Databricks File System (DBFS) public paths. Got `AccessDeniedException` - workspace has DBFS public access disabled for security.

### Solution

Use **Unity Catalog Volumes** instead of DBFS:

```python
# WRONG: Public DBFS paths don't work
INBOX_PATH = "/dbfs/FileStore/inbox"

# RIGHT: Use Unity Catalog Volumes
CATALOG = "workspace"
SCHEMA = "dbxloader"
VOLUME = "files"
INBOX_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}/inbox"
```

### Key Insights

1. Unity Catalog Volumes use `/Volumes/catalog/schema/volume_name/path` format
2. File operations (`dbutils.fs.ls()`, `dbutils.fs.mv()`) work identically
3. Volumes provide fine-grained access control and audit logging

### Recommendation

For any Databricks project, default to Unity Catalog Volumes for all file storage. Never hardcode `/dbfs/` paths.

---

## Lesson 89: Schema Type Mismatch INT vs BIGINT from Spark SQL Introspection

**Date**: 2026-01-24
**Project**: dbxloader (Databricks POC)
**Category**: Spark, Schema, SQL, Type Systems

### Problem

Created config table with `ordinal_position INT`. When reading via PySpark and writing back, got schema mismatch error - Spark SQL introspection returns BIGINT instead of INT.

### Solution

Use SQL INSERT instead of DataFrame.write() for type coercion:

```python
# WRONG: DataFrame.write() requires exact schema match
df.write.mode("append").saveAsTable(STAGING_TABLE)

# RIGHT: SQL INSERT handles type coercion
spark.sql(f"INSERT INTO {STAGING_TABLE} SELECT ... FROM temp_view")
```

### Key Insights

1. Spark's SQL engine coerces compatible types during INSERT
2. DataFrame.write() is stricter about exact schema match
3. Spark prefers BIGINT internally for numeric columns

### Recommendation

For Delta table writes in Databricks, prefer SQL INSERT over DataFrame.write() when schema precision matters.

---

## Lesson 90: Decimal Precision Must Be Consistent Across Config and Table Schema

**Date**: 2026-01-24
**Project**: dbxloader (Databricks POC)
**Category**: Data Types, Schema, Configuration

### Problem

Config table stored just `DECIMAL` without precision/scale. Loading `coupon_rate: 1234.5678` got truncated to `1234.56` due to default `DECIMAL(18,2)`.

### Solution

For MVP, hardcode precision overrides per column:

```python
DECIMAL_OVERRIDES = {
    "coupon_rate": (10, 4),
    "market_cap": (18, 2),
}

def get_decimal_precision(column_name: str) -> tuple[int, int]:
    return DECIMAL_OVERRIDES.get(column_name, (18, 2))
```

### Key Insights

1. DECIMAL(P,S): P=total digits, S=digits after decimal
2. Spark doesn't auto-coerce between different DECIMAL precisions
3. MVP hardcodes overrides; Phase 2 adds to config table

### Recommendation

Document all DECIMAL columns with their required precision. For MVP, use hardcoded mapping; for production, extend config table schema.

---

## Lesson 91: Null Checking in Arrays Must Use filter() Expression

**Date**: 2026-01-24
**Project**: dbxloader (Databricks POC)
**Category**: Spark, SQL, Array Operations, Null Handling

### Problem

Built validation logic collecting columns with NULL values into array. Result was `[null, null, null]` for valid rows instead of `[]`. Array of NULLs is not empty!

### Solution

Use `filter()` expression to remove NULLs:

```python
# WRONG: Array contains null elements
validated_df = df.withColumn("_null_failures", F.array(
    F.when(F.col("col1").isNull(), F.lit("col1")),
    F.when(F.col("col2").isNull(), F.lit("col2"))
))

# RIGHT: Filter out NULLs
validated_df = df.withColumn(
    "_null_failures",
    F.expr("filter(array(...), x -> x IS NOT NULL)")
)
```

### Key Insights

1. `[null, null].isNotNull()` returns TRUE - the array exists
2. `filter(arr, x -> x IS NOT NULL)` removes null elements
3. Use `F.size(F.col("arr")) > 0` to check for failures

### Recommendation

When collecting optional values into arrays in Spark, always filter NULLs using `F.expr("filter(...)")`.

---

## Lesson 92: Widget Defaults Must Match Actual File Names in Volume

**Date**: 2026-01-24
**Project**: dbxloader (Databricks POC)
**Category**: Databricks, Notebooks, File Handling

### Problem

Notebook widget default `"Training (1).csv"` didn't match actual uploaded file `"Training.csv"`. DBFS/Volumes are case-sensitive.

### Solution

Verify uploaded file names before setting widget defaults:

```python
# List actual files in inbox
inbox_files = dbutils.fs.ls(INBOX_PATH)
for f in inbox_files:
    print(f"  {f.name}")

# Set widget to actual file name
actual_file_name = inbox_files[0].name if inbox_files else "default.csv"
dbutils.widgets.text("file_name", actual_file_name, "File Name")
```

### Key Insights

1. Databricks Volumes are case-sensitive (like Unix)
2. Special characters in filenames (spaces, parens) are allowed but must match exactly
3. Startup validation should verify file exists before processing

### Recommendation

After uploading files to a volume, verify exact file names and update widget defaults. Include file existence check in startup validation.

---

## Lesson 93: Databricks Workspace May Only Support Serverless Compute

**Date**: 2026-01-24
**Project**: dbxloader (Databricks POC)
**Category**: Databricks, Infrastructure, Compute

### Problem

Attempted to create traditional Databricks cluster. Got error: workspace only supports serverless compute - cannot create classic clusters.

### Solution

Use Databricks Workflows with serverless compute:

```bash
databricks jobs submit --json '{
  "run_name": "dbxloader-job",
  "tasks": [{
    "task_key": "load_data",
    "notebook_task": {
      "notebook_path": "/Repos/user/dbxloader/notebooks/01_loader",
      "source": "WORKSPACE"
    }
  }]
}'
```

### Key Insights

1. Serverless: no cluster management, automatic scaling
2. Notebooks, Jobs, and Workflows all run serverless
3. Workspace-level configuration set by admin

### Recommendation

Check workspace compute type (Admin Console → Settings). Design notebooks as reusable task components for Workflows.

---

## Lesson 94: Validation Logic Needs Explicit Boolean Columns

**Date**: 2026-01-24
**Project**: dbxloader (Databricks POC)
**Category**: Spark, Validation, Logic

### Problem

Filtered valid/invalid rows using `isNull()` on failure array. Both filters returned 0 rows - semantic confusion between NULL array vs empty array.

### Solution

Add explicit boolean validation column:

```python
# Add explicit boolean
validated_df = df.withColumn("_null_count", sum(null_check_exprs))
validated_df = validated_df.withColumn("_is_valid", F.col("_null_count") == 0)

# Filter on boolean (reliable!)
valid_df = validated_df.filter(F.col("_is_valid") == True)
error_df = validated_df.filter(F.col("_is_valid") == False)
```

### Key Insights

1. Boolean columns are clearer than NULL/not-NULL semantics
2. Separate concerns: `_null_failures` (diagnostic), `_null_count` (metric), `_is_valid` (decision)
3. Always filter on boolean, never on NULL/not-NULL

### Recommendation

For validation logic in Spark, create explicit boolean `_is_valid` column. Keep diagnostic arrays for error reporting.

---

## Lesson 95: Config-Driven Data Loading Pattern for Databricks

**Date**: 2026-01-24
**Project**: dbxloader (Databricks POC)
**Category**: Architecture, Data Engineering, Reusability

### Pattern

Build a **single, reusable data loader** that processes any CSV by reading configuration from a Delta table. No code changes for new data sources.

### Core Components

1. **Configuration Table**: Defines column mappings, types, null constraints
2. **Unified Loader**: Reads config and applies transformations
3. **Add New Source**: Just INSERT rows to config table

```sql
-- Add new data source (no code changes!)
INSERT INTO config.loader_mapping VALUES
    ('orders', 'Order ID', 'order_id', 'VARCHAR', false, 1),
    ('orders', 'Amount', 'amount', 'DECIMAL', true, 2);
```

### Key Benefits

| Traditional | Config-Driven |
|-------------|---------------|
| New notebook per source | Insert config rows |
| Type changes = redeploy | DB update only |
| Hardcoded validation | Config-driven |

### Recommendation

For Databricks data engineering:
1. Start with config-driven architecture
2. Separate static config (code) from dynamic config (tables)
3. Use fail-fast validation with clear error messages
4. Always archive processed files for audit trail

---

## Lesson 96: Stress Test P&L Calculation - Weight Normalization Required

**Date**: 2026-01-25
**Project**: Matrix Risk Engine
**Category**: Risk Calculation, Financial Math, Bug Prevention

### Problem

The `stress_test()` method in OREAdapter used `positions * price * shock` which showed a -$112M loss on a $10M portfolio - completely impossible.

### Root Cause

Mixing units: positions were already in dollar terms (`{"AAPL": $2,000,000}`), but the code multiplied by price again, double-counting position size.

```python
# WRONG - positions are already in dollars
for symbol, position in portfolio.positions.items():
    pnl += position * current_price * shock  # Double-counts!
```

### Solution

Use weight-normalized formula where weights are percentages of NAV:

```python
# CORRECT - use weights as percentages of NAV
base_npv = portfolio.nav  # $10,000,000
for symbol, weight in portfolio.weights.items():
    shock = scenario.shocks.get(symbol, 0)
    pnl += base_npv * weight * shock
# Example: $10M * 0.20 * -0.10 = -$200K loss for 20% position with 10% drop
```

### Evidence

`/Users/naidooone/Developer/projects/openriskengine/src/adapters/ore_adapter.py` lines 264-329

### Prevention Checklist

- [ ] Always verify units in financial calculations (dollars vs shares vs percentages)
- [ ] Sanity check: stress test loss should be proportional to shock magnitude
- [ ] Add assertion: `abs(pct_change) <= abs(max_shock) * 1.1` (allow 10% margin)
- [ ] Write functional validation tests that check results against known scenarios

---

## Lesson 97: Functional Validation Over Unit Test Coverage

**Date**: 2026-01-25
**Project**: Matrix Risk Engine
**Category**: Testing, Quality Assurance, Risk Models

### Problem

Attempted to increase test coverage from 54% to 80% by adding 5 new test files. All failed due to API mismatches between test assumptions and actual implementations. Coverage remained at 54%.

### Key Finding

Functional validation scripts caught the stress test bug (Lesson 96) that unit tests would have missed. The scripts test real workflows end-to-end with realistic data.

### Solution

For complex financial calculations, prioritize:

1. **Functional tests** that exercise real workflows end-to-end
2. **Historical scenario replay** (known market events with documented outcomes)
3. **Model backtesting** (VaR predictions vs actual losses)

### Scripts Created

```
scripts/
├── var_backtest.py           # Kupiec POF test for VaR model validation
├── historical_scenarios.py   # Replay 2008 Crisis, COVID crash, Black Monday
└── risk_validation_report.py # Comprehensive report (VaR, CVaR, Greeks, attribution)
```

### Evidence

- `/Users/naidooone/Developer/projects/openriskengine/scripts/var_backtest.py`
- `/Users/naidooone/Developer/projects/openriskengine/scripts/historical_scenarios.py`
- `/Users/naidooone/Developer/projects/openriskengine/scripts/risk_validation_report.py`

### Prevention Checklist

- [ ] Before adding unit tests, read actual implementation code first
- [ ] Create functional validation scripts for financial calculations
- [ ] Run historical scenario replay after any risk calculation changes
- [ ] Don't chase coverage percentage - focus on testing actual behavior

---

## Lesson 98: Module Import in Scripts Directory

**Date**: 2026-01-25
**Project**: Matrix Risk Engine
**Category**: Python, Project Structure

### Problem

Scripts in `scripts/` directory couldn't import from `src/` package:

```
ModuleNotFoundError: No module named 'src'
```

### Solution

Add at top of each script before imports:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now this works:
from src.adapters.ore_adapter import OREAdapter
```

### Better Long-term Solution

Use development mode installation:

```bash
pip install -e .
```

This requires a proper `pyproject.toml` or `setup.py` with package configuration.

### Evidence

All scripts in `/Users/naidooone/Developer/projects/openriskengine/scripts/` use this pattern.

### Prevention Checklist

- [ ] Add path setup boilerplate to all scripts in `scripts/` directory
- [ ] Consider using `pip install -e .` for proper package installation
- [ ] Document import requirements in script headers
- [ ] Add a scripts README explaining how to run them

---

## Lesson 99: VaR Model Validation - Kupiec POF Test

**Date**: 2026-01-25
**Project**: Matrix Risk Engine
**Category**: Risk Models, Statistical Validation

### Learning

After implementing VaR, validate it using the **Kupiec Proportion of Failures (POF) test**:

- For 95% VaR: expect ~5% of days to breach (actual loss > VaR estimate)
- For 99% VaR: expect ~1% of days to breach

### Implementation

```python
# Calculate breach statistics
expected_breach_rate = 1 - confidence_level  # e.g., 0.05 for 95% VaR
actual_breach_rate = num_breaches / total_days

# Kupiec LR statistic (should be < 3.84 for 95% confidence)
p = expected_breach_rate
x = num_breaches
n = total_days

lr_pof = -2 * (
    x * np.log(p / (x/n)) + (n-x) * np.log((1-p) / (1-x/n))
)

# Model is valid if lr_pof <= 3.84 (chi-squared critical value at 95%)
model_valid = lr_pof <= 3.84
```

### Interpretation

| Breach Rate Ratio | Interpretation |
|-------------------|----------------|
| 0.8 - 1.2 | Well-calibrated model |
| < 0.8 | Too conservative (fewer breaches than expected) |
| > 1.2 | Underestimates risk (more breaches than expected) |

### Evidence

`/Users/naidooone/Developer/projects/openriskengine/scripts/var_backtest.py` implements Kupiec POF test.

### Prevention Checklist

- [ ] Run VaR backtest after any risk model changes
- [ ] Breach rate should be within 20% of expected rate
- [ ] Check for breach clustering (independence test)
- [ ] Document model validation results in risk reports

---

## Lesson 100: Hexagonal Architecture for External C++ Libraries

**Date**: 2026-01-25
**Project**: Matrix Risk Engine
**Category**: Architecture, Testing, External Dependencies

### Benefit

The `RiskPort` protocol interface isolated risk logic from `OREAdapter`:

- `StubOREAdapter` enables unit testing without installing C++ ORE libraries
- Tests run in milliseconds (stubs) vs seconds (actual ORE)
- CI/CD doesn't need heavy C++ dependencies

### Pattern

```python
# Port (interface) - src/core/ports/risk_port.py
class RiskPort(Protocol):
    def calculate_var(self, portfolio, market_data, ...) -> dict: ...
    def stress_test(self, portfolio, market_data, scenarios) -> pd.DataFrame: ...

# Adapter (implementation) - src/adapters/ore_adapter.py
class OREAdapter:  # implements RiskPort
    def calculate_var(self, portfolio, market_data, ...) -> dict:
        # Real ORE C++ implementation via SWIG bindings
        ore = self._get_ore()
        ...

# Stub (testing) - tests/stubs/stub_ore_adapter.py
class StubOREAdapter:  # also implements RiskPort
    def calculate_var(self, portfolio, market_data, ...) -> dict:
        return {"95%": -50000, "99%": -75000}  # Fixed test values
```

### Evidence

- Port: `/Users/naidooone/Developer/projects/openriskengine/src/core/ports/risk_port.py`
- Adapter: `/Users/naidooone/Developer/projects/openriskengine/src/adapters/ore_adapter.py`
- Stub: `/Users/naidooone/Developer/projects/openriskengine/tests/stubs/stub_ore_adapter.py`

### Prevention Checklist

- [ ] Define ports as Protocol classes in `src/core/ports/`
- [ ] Adapters in `src/adapters/` implement ports
- [ ] Create stubs in `tests/stubs/` for unit testing
- [ ] Never import adapters directly in core domain code
- [ ] For C++/external libraries, lazy-load with fallback to pure Python

---

## Lesson 101: Parallel Agent Execution for Large Feature Implementation

**Date**: 2026-01-26
**Project**: Agentic HUD Extension
**Category**: Agentic Development, Productivity

### Context

Implementing a 20-capability extension with 7 services, 4 ports, 4 adapters, and 44 tasks would traditionally take many sequential iterations.

### Discovery

Launching multiple Task agents in parallel dramatically accelerates implementation:

```
# Sequential: ~6 hours for 44 tasks
# Parallel: ~1.5 hours with 6 agents running concurrently
```

### Pattern

```python
# Launch 6 independent agents in a single message
<function_calls>
<invoke name="Task" subagent_type="general-purpose" prompt="Implement P12 FileSystemPort..."/>
<invoke name="Task" subagent_type="general-purpose" prompt="Implement P13 ProjectIndexStoragePort..."/>
<invoke name="Task" subagent_type="general-purpose" prompt="Implement P14 TaskSnapshotStoragePort..."/>
<invoke name="Task" subagent_type="general-purpose" prompt="Implement C12 ProjectDiscoveryService..."/>
<invoke name="Task" subagent_type="general-purpose" prompt="Implement C13 ArtifactParser..."/>
<invoke name="Task" subagent_type="general-purpose" prompt="Update schema with all tables..."/>
</function_calls>
```

### Key Insight

Agents that don't have dependencies on each other can run concurrently. Group tasks by dependency level:
- **Wave 1**: Ports (no dependencies)
- **Wave 2**: Adapters + Domain Models (depend on ports)
- **Wave 3**: Services (depend on adapters)
- **Wave 4**: MCP Tools + Dashboard (depend on services)

### Evidence

- 50 files, 25,082 lines added in ~2 hours with parallel execution
- 621 tests passing, 81% coverage
- Commit: `6ec06f6` in agentic_hud

### Prevention Checklist

- [ ] Identify independent tasks that can run in parallel
- [ ] Launch 4-6 agents per wave (balance parallelism vs context)
- [ ] Include spec/artifact references in each agent prompt
- [ ] Wait for all agents before starting dependent wave
- [ ] Verify imports and run tests after each wave

---

## Lesson 102: Solution Designer → BA → Coding Agent Pipeline

**Date**: 2026-01-26
**Project**: Agentic HUD Extension
**Category**: Agentic Development, Process

### Context

Large features (20+ capabilities) benefit from structured handoff between specialized agents.

### Discovery

The three-agent pipeline produces implementation-ready artifacts:

1. **Solution Designer** → Comprehensive spec with flows, domain objects, security threats
2. **BA Agent** → Tasklist with dependencies, acceptance criteria, evidence requirements
3. **Coding Agents** → Parallel implementation following tasklist order

### Pattern

```
User Request
    ↓
Solution Designer (research + design)
    ↓ Handoff Envelope (spec.md)
BA Agent (decomposition)
    ↓ Artifacts (tasklist.md, rules.yaml, quality_gates.md)
Parallel Coding Agents (implementation)
    ↓ Code + Tests
QA Reviewer (verification)
```

### Handoff Envelope Contents

```yaml
project_slug: "agentic_hub_extension"
problem_statement: "Developers lack consolidated view..."
stakeholders: [Developer, Claude_Code_Agent]
in_scope: [project_discovery, artifact_parsing, ...]
out_of_scope: [multi-user, ML predictions, ...]
key_flows: [F1, F2, F3, ...]
domain_objects: [ProjectIndex, TaskSnapshot, ...]
components: {core: [C12-C18], ports: [P12-P15], adapters: [A12-A15]}
risks: [T9-T13 with controls]
recommended_next_agent: "BA"
```

### Evidence

- Solution design: `agentic_hub_extension_spec.md` (96KB, 1229 lines)
- BA artifacts: `tasklist.md` (50KB, 44 tasks), `rules.yaml` (9KB), `quality_gates.md` (20KB)
- Implementation: 7 services, 4 ports, 4 adapters, 8 MCP tools, 5 dashboard tabs

### Prevention Checklist

- [ ] Always start large features with design agent
- [ ] Include security threat model in spec (T1, T2, ... with CTRL controls)
- [ ] BA tasklist should have 30-120 minute tasks with blockedBy fields
- [ ] Each task needs acceptance criteria and evidence requirements
- [ ] Coding agents should reference tasklist task IDs

---

## Lesson 103: Extension Pattern - Extend Don't Modify Core

**Date**: 2026-01-26
**Project**: Agentic HUD Extension
**Category**: Architecture, Hexagonal

### Context

Adding 20 new capabilities to an existing system with 11 components and 257 tests.

### Discovery

Extending without modifying core components preserves stability:

```
Existing: C1-C11, P1-P11, A1-A11 (untouched)
Extension: C12-C18, P12-P15, A12-A15 (new)
```

### Pattern

```python
# DON'T modify existing components
class SessionAggregator:  # C2 - unchanged
    pass

# DO create extension components that use existing ports
class SessionProjectAttributor:  # C17 - new
    def __init__(self, span_storage: SpanStoragePort):  # Reuses P1
        self.span_storage = span_storage

    def attribute_session_to_project(self, session_id: str, spans: list[Span]) -> str | None:
        # New functionality using existing span data
        pass
```

### Benefits

- Original 257 tests continue passing
- No regression risk in existing functionality
- Clear separation of concerns
- Extension can be disabled without affecting core

### Evidence

- All 257 original tests passed after extension
- New tests: 374+ (621 total)
- Schema uses separate tables with foreign keys (not modifying existing tables)

### Prevention Checklist

- [ ] Number new components to continue existing sequence (C12, not C1a)
- [ ] Reuse existing ports when possible (P1, P2, P6, P7)
- [ ] Create new ports only for new capabilities
- [ ] Add new schema tables with foreign keys, don't modify existing
- [ ] Run full test suite after each extension component

---

## Lesson 104: MCP Tool Token Budget Enforcement

**Date**: 2026-01-26
**Project**: Agentic HUD Extension
**Category**: MCP, API Design

### Context

MCP tools must return <200 tokens to avoid overwhelming Claude's context.

### Discovery

Token budget requires deliberate response design:

```python
# BAD: Unlimited response
def get_project_status(project_id: str) -> dict:
    return project.model_dump()  # Could be 500+ tokens

# GOOD: Token-conscious response
def get_project_status(project_id: str) -> dict:
    return {
        "project_id": project.project_id,
        "name": project.project_name[:50],  # Truncate
        "type": project.project_type.value,
        "health_score": round(project.completion_rate, 2),
        "tasks": f"{project.completed_tasks}/{project.total_tasks}",
        # Omit verbose fields
    }
```

### Token Budget Strategies

| Strategy | Example |
|----------|---------|
| Truncate strings | `title[:50]` |
| Limit list items | `projects[:20]` |
| Round floats | `round(score, 2)` |
| Omit verbose fields | Skip `parsed_data` JSON |
| Use compact formats | `"3/5"` instead of `{"completed": 3, "total": 5}` |

### Evidence

- All 8 new MCP tools verified to return <200 tokens
- `hud.check_project_health`: <150 tokens
- `hud.get_project_metrics`: <100 tokens

### Prevention Checklist

- [ ] Define token budget per tool in spec (default: 200)
- [ ] Test tool output token count in unit tests
- [ ] Truncate strings at 50 chars for titles, 100 for summaries
- [ ] Limit list responses to 20 items max
- [ ] Use error responses under 50 tokens

---

## Lesson 105: Composite Health Score Design Pattern

**Date**: 2026-01-26
**Project**: Agentic HUD Extension
**Category**: Domain Modeling, Metrics

### Context

Project health needs to aggregate multiple signals into a single actionable metric.

### Discovery

Weighted composite scores with component breakdown enable both quick assessment and drill-down:

```python
health_score = (
    0.4 * completion_health +   # Task completion rate
    0.2 * drift_health +        # Files modified in scope
    0.2 * documentation_health + # Doc coverage
    0.2 * activity_health        # Recency of work
)
```

### Component Calculations

| Component | Formula | Range |
|-----------|---------|-------|
| `completion_health` | `completed_tasks / total_tasks` | 0.0-1.0 |
| `drift_health` | `1.0 - (drift_count / max_files)` | 0.0-1.0 |
| `documentation_health` | `min(doc_count / expected, 1.0)` | 0.0-1.0 |
| `activity_health` | Decay function based on `last_activity` age | 0.0-1.0 |

### Activity Decay Function

```python
def calculate_activity_health(last_activity: datetime) -> float:
    days_ago = (now - last_activity).days
    if days_ago < 7: return 1.0
    if days_ago < 30: return 0.7
    if days_ago < 90: return 0.4
    return 0.1
```

### Health Flags

Complement numeric score with actionable flags:
- `no_recent_activity`: last_activity > 90 days
- `high_drift`: drift_count > 5
- `missing_docs`: doc_count < 2
- `low_completion`: completion_rate < 0.5

### Evidence

- `ProjectHealthCalculator` service: 34 unit tests
- Used by dashboard Health tab and `hud.check_project_health` MCP tool

### Prevention Checklist

- [ ] Make weights configurable (rules.yaml)
- [ ] Clamp all component scores to 0.0-1.0
- [ ] Include both numeric score AND human-readable flags
- [ ] Recalculate on demand (don't cache stale health)
- [ ] Document weight rationale in rules.yaml comments

---

## Lesson 106: Documentation System Integration Pattern

**Date**: 2026-01-26
**Project**: Loader4 + Agentic HUD Extension
**Category**: Architecture, Documentation

### Context

Projects need a centralized documentation system that survives context compression and enables cross-project visibility.

### Discovery

A manifest-based documentation system with project-level CONTEXT.md files enables:
1. Session restart context recovery
2. Cross-project document aggregation
3. Structured metadata for dashboards

### Pattern

```
~/Developer/docs/                    # Global documentation root
├── index/
│   ├── global_manifest.json        # Aggregated from all projects
│   └── projects.json               # Project registry
├── schema/
│   └── manifest.schema.json        # JSON Schema for validation
└── templates/
    └── CONTEXT.template.md         # Template for project context

~/Developer/projects/{project}/docs/
├── manifest.json                    # Project-specific metadata
├── CONTEXT.md                       # Session restart context
├── technical/                       # Technical docs
├── solutions/                       # Solution proposals
└── generated/                       # HTML output
```

### CONTEXT.md Structure

```markdown
# Project Context: {Project Name}

## Quick Reference
| Field | Value |
| Project | ... |
| Status | ... |
| Last Session | ... |

## Session Restart Prompt
\`\`\`
Copy this to resume context in new session...
\`\`\`

## Key Decisions Made
| Decision | Rationale | Date |

## Open Questions
## Next Actions
```

### Evidence

- Loader4: `docs/CONTEXT.md`, `docs/manifest.json`
- Global: `~/Developer/docs/index/global_manifest.json`
- Integration: `DocumentationSyncService` (C15), `hud.query_documentation` MCP tool

### Prevention Checklist

- [ ] Every project gets `docs/CONTEXT.md` and `docs/manifest.json`
- [ ] Update CONTEXT.md at end of each major session
- [ ] Run aggregation after adding new documents
- [ ] Include session restart prompt in CONTEXT.md
- [ ] Store key decisions with rationale and date

---

## Lesson 107: Centralize Time & UUID Port Definitions to Prevent Determinism Violations

**Date**: 2026-01-26
**Project**: agentic_hud
**Category**: Architecture, Testing, Dependency Injection, Determinism

### Problem

Fixed determinism violations across 14+ core services where each service independently called `datetime.now(UTC)` and `uuid4()` directly, making them impossible to test deterministically.

**Anti-pattern that spread easily:**
- Each service defined its own `TimePort` and `DefaultTimePort` locally
- This created duplication and made it easy to forget to use the port
- Direct calls like `datetime.now(UTC)` bypassed injection entirely
- Tests could not control time values (timestamp fields in events, records, etc.)

### Root Cause

1. Original services used system time/UUID directly for convenience
2. Tests couldn't control these values, making them flaky
3. No shared port interface meant each service reinvented the wheel
4. Code reviews didn't catch the duplication pattern

### Solution

**Step 1: Centralize port definitions in a single module**

Created `core/ports/time.py`:

```python
from typing import Protocol
from datetime import datetime, timezone
from uuid import uuid4

class TimePort(Protocol):
    def now(self) -> datetime: ...

class UUIDPort(Protocol):
    def generate(self) -> str: ...

class DefaultTimePort:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)

class DefaultUUIDPort:
    def generate(self) -> str:
        return str(uuid4())
```

**Step 2: Update all services to inject ports**

```python
# BEFORE - BAD
class EventService:
    def create_event(self) -> Event:
        return Event(id=str(uuid4()), timestamp=datetime.now(timezone.utc))

# AFTER - GOOD
class EventService:
    def __init__(self, time_port: TimePort | None = None, uuid_port: UUIDPort | None = None):
        self._time_port = time_port or DefaultTimePort()
        self._uuid_port = uuid_port or DefaultUUIDPort()

    def create_event(self) -> Event:
        return Event(id=self._uuid_port.generate(), timestamp=self._time_port.now())
```

**Step 3: Handle dataclass default_factory**

```python
_default_time_port = DefaultTimePort()

@dataclass
class Event:
    timestamp: datetime = field(default_factory=lambda: _default_time_port.now())
```

### Detection Strategy

```bash
grep -r "datetime\.now\|uuid4" src/project/core/services/ --include="*.py" | grep -v import
```

Count should be zero.

### Quality Gate

```bash
violations=$(grep -r "datetime\.now\|uuid4" src/project/core/services/ --include="*.py" | grep -v import | wc -l)
[ "$violations" -eq 0 ] && echo "PASS" || echo "FAIL: $violations violations"
```

### Key Insight

**Centralization prevents drift.** When each service defines its own ports, some will eventually just call `datetime.now()` directly. A centralized module makes the pattern obvious and violations scannable.

---

## Lesson 108: API Response Contracts Must Be Validated at Integration Points

**Date**: 2026-01-26
**Project**: agentic_hud
**Category**: API Design, Integration Testing, Type Safety

### Problem

Found 5 critical field mismatches between CLI callbacks and UI JavaScript in agentic_hud dashboard:

1. CLI returns `last_updated` but UI expects `updated`
2. Projects API missing fields: `health_score`, `session_count`, `total_tokens`, `has_rules`, `has_quality_gates`
3. Docs API missing `word_count` field that UI renders

**Impact**: 3 of 6 dashboard pages had broken/missing data with no error indication.

### Root Cause

- API response schemas not defined or validated
- No contract testing between backend and frontend
- UI discovered missing fields through broken renders, not tests
- Defensive coding (`field || 0`) hid the bugs

### Solution

**Step 1: Define response models explicitly**

```python
from pydantic import BaseModel

class ProjectResponse(BaseModel):
    project_id: str
    project_name: str
    health_score: float  # 0.0-1.0
    session_count: int
    total_tokens: int
    has_rules: bool
    has_quality_gates: bool
```

**Step 2: Write integration tests for field presence**

```python
def test_projects_response_has_all_required_fields():
    response = client.get("/api/projects")
    for project in response.json():
        # This will fail if any field is missing
        ProjectResponse(**project)
```

**Step 3: Generate TypeScript types from Pydantic**

Never hand-write TypeScript interfaces. Use `pydantic-to-typescript` or similar.

### Detection Strategy

```bash
# Find all API callback functions
grep -r "def get_.*_data" src/cli.py

# For each, verify Pydantic model exists and is used
```

### Quality Gate

- All API endpoints have a defined Pydantic response model
- Integration test validates ALL schema fields are present
- TypeScript types are generated, not hand-written

---

## Lesson 109: Filter Parameters Require Type-Checked Function Signatures

**Date**: 2026-01-26
**Project**: agentic_hud
**Category**: API Design, Type Safety, Integration Testing

### Problem

Drift time filter was completely broken:
- Function signature: `def get_drift_data(project_id: str)`
- Adapter called it: `adapter._drift_callback(project_id, days)`
- The `days` parameter was silently dropped!

**Impact**: Time range filter UI had zero effect - users thought they were filtering but got all data.

### Root Cause

- Python doesn't enforce function signature matching at runtime
- No type checking on callback assignment
- No integration test verifying filter actually works

### Solution

**Step 1: Use Protocol-based typing**

```python
from typing import Protocol

class DriftCallback(Protocol):
    def __call__(self, project_id: str | None, days: int) -> list[dict]: ...

class WebAdapter:
    _drift_callback: DriftCallback | None = None
    
    def set_drift_callback(self, callback: DriftCallback) -> None:
        self._drift_callback = callback
```

**Step 2: Run mypy --strict**

```bash
mypy --strict src/adapters/web/perspective_adapter.py
```

This will catch signature mismatches at development time.

**Step 3: Write filter behavior tests**

```python
def test_drift_filter_days_parameter_actually_filters():
    # Create data spanning 60 days
    # Filter for last 7 days
    result = get_drift_data(project_id="test", days=7)
    # Verify ONLY last 7 days of data returned
    for event in result:
        assert event["snapshot_time"] > (now - timedelta(days=7))
```

### Detection Strategy

```bash
# Find callback setters
grep -r "set_.*_callback" src/

# Verify each has Protocol type hint
```

### Quality Gate

- mypy --strict passes on all adapter code
- Every filter parameter has an integration test
- Test verifies parameter changes the results

---

## Lesson 110: Defensive Coding Without Observability Hides Data Flow Bugs

**Date**: 2026-01-26
**Project**: agentic_hud
**Category**: Observability, Debugging, Error Handling

### Problem

UI used fallback values that hid missing data:
```javascript
const healthy = projects.filter(p => (p.health_score || 0.5) >= 0.7).length;
const sessions = p.session_count || 0;
```

**Impact**: Bugs went undetected for weeks because defaults looked reasonable.

### Root Cause

- Defensive coding without corresponding logging
- No distinction between "field is zero" and "field is missing"
- Silent fallbacks in production code

### Solution

**Step 1: Validate response schema on receipt**

```javascript
function validateProjectResponse(project) {
    const required = ['health_score', 'session_count', 'total_tokens'];
    const missing = required.filter(f => !(f in project));
    if (missing.length > 0) {
        console.error('Missing fields in project response:', missing, project);
        // In dev mode, throw; in prod, report to error tracking
    }
}
```

**Step 2: Log every fallback usage**

```javascript
function getWithFallback(obj, field, fallback) {
    if (!(field in obj)) {
        console.warn(`Using fallback for missing field: ${field}`);
        errorTracking.captureMessage(`Missing field: ${field}`);
    }
    return obj[field] ?? fallback;
}
```

**Step 3: Use explicit null vs zero in types**

```typescript
interface Project {
    health_score: number | null;  // null = not calculated
    session_count: number;        // 0 is valid value
}
```

### Detection Strategy

```bash
# Find fallback patterns
grep -r "|| 0\||| 0.5\|?? 0" src/components/
```

### Quality Gate

- Zero `|| defaultValue` patterns without corresponding error logging
- Response validation on all API calls in development mode
- Error tracking configured for missing field alerts

---

## Lesson 111: Business Logic Duplication Creates Divergence Risk

**Date**: 2026-01-26
**Project**: agentic_hud
**Category**: Architecture, DRY, Business Logic

### Problem

Health flags were calculated in two places with potentially different thresholds:

**Backend (ProjectHealthCalculator):**
```python
FLAG_HIGH_DRIFT_COUNT: int = 5
if project.drift_count > FLAG_HIGH_DRIFT_COUNT:
    flags.append("high_drift")
```

**Frontend (JavaScript):**
```javascript
if ((p.drift_count || 0) > 5) {
    flags.push({ type: 'danger', icon: '⚡', text: '...' });
}
```

**Impact**: Thresholds could diverge silently. Maintenance burden doubled.

### Root Cause

- UI built before backend logic was complete
- No shared configuration source
- "Quick fix" became permanent

### Solution

**Step 1: Centralize thresholds in config**

```yaml
# health_rules.yaml
thresholds:
  high_drift_count: 5
  low_completion_rate: 0.5
  stale_activity_days: 90
```

**Step 2: Backend calculates everything, returns complete data**

```python
def get_project_response(project):
    health = calculator.calculate_health_score(project)
    return {
        "health_score": health.health_score,
        "health_flags": health.flags,  # Backend-calculated flags
        "thresholds_used": health.thresholds,  # Transparency
    }
```

**Step 3: Frontend only displays, never recalculates**

```javascript
// GOOD: Display what backend calculated
<HealthFlags flags={project.health_flags} />

// BAD: Recalculate in frontend
const isHighDrift = project.drift_count > 5;  // DON'T DO THIS
```

### Detection Strategy

```bash
# Find frontend calculations
grep -r "drift_count\|completion_rate\|health" src/components/ | grep -v "props\|response"
```

### Quality Gate

- Zero business logic calculations in frontend components
- All thresholds sourced from single config file
- Backend returns pre-calculated flags and scores

---

## Lesson 112: UI Controls Without Backend Integration Tests Are Dead Code

**Date**: 2026-01-26
**Project**: agentic_hud
**Category**: Testing, UI/UX, Integration

### Problem

Task Timeline status filter dropdown was built but never worked:
- UI control existed and looked functional
- User could select different statuses
- Results never changed because backend didn't read the filter

**Impact**: Users thought feature worked but it was completely non-functional.

### Root Cause

- UI built in isolation without backend integration
- No integration test verifying filter → API → results flow
- Code review only checked UI looked correct

### Solution

**Step 1: Write integration test BEFORE implementing UI control**

```python
def test_task_status_filter_changes_results():
    # Create tasks with different statuses
    create_task(status="pending")
    create_task(status="completed")
    
    # Filter by status
    result = get_tasks(status_filter="pending")
    
    # Verify filter applied
    assert all(t["status"] == "pending" for t in result)
```

**Step 2: Define contract between UI and API**

```yaml
# filter_contracts.yaml
task_timeline:
  status_filter:
    ui_element: "#task-filter-status"
    api_param: "status"
    valid_values: ["all", "pending", "in_progress", "completed", "blocked"]
```

**Step 3: E2E test for complete flow**

```javascript
test('status filter changes displayed tasks', async () => {
    await page.selectOption('#task-filter-status', 'completed');
    await page.waitForResponse('/api/tasks*');
    const rows = await page.$$('.task-row');
    for (const row of rows) {
        expect(await row.textContent()).toContain('completed');
    }
});
```

### Detection Strategy

```bash
# Find UI controls
grep -r "select\|filter" src/components/ --include="*.tsx"

# For each, verify integration test exists
```

### Quality Gate

- Every UI filter control has integration test
- Test verifies: UI action → API parameter → filtered results
- E2E test covers user interaction to result display

---

## Lesson 113: Runtime Contract Validation for Dynamic API Responses

**Date**: 2026-01-26
**Project**: agentic_hud
**Category**: Type Safety, Runtime Validation, API Design

### Problem

Fields defined in Pydantic models were never actually returned:
- Model declared `health_score: float`
- API callback didn't include `health_score` in response dict
- Type checking passed but runtime response was incomplete

**Impact**: Type-level validation gave false confidence; actual responses were broken.

### Root Cause

- Pydantic models existed but weren't enforced on response construction
- No runtime validation that response matched schema
- Gap between "schema exists" and "schema is used"

### Solution

**Step 1: Use response_model in API routes**

```python
@app.get("/api/projects", response_model=list[ProjectResponse])
def get_projects():
    # FastAPI will validate response matches ProjectResponse
    return projects_data
```

**Step 2: Validate in callback construction**

```python
def get_projects_data() -> list[dict]:
    projects = query_projects()
    responses = []
    for p in projects:
        response = ProjectResponse(
            project_id=p.project_id,
            health_score=p.health_score,
            # ... all fields
        )
        responses.append(response.model_dump())
    return responses
```

**Step 3: Frontend runtime validation with zod**

```typescript
const ProjectSchema = z.object({
    project_id: z.string(),
    health_score: z.number(),
    session_count: z.number(),
});

async function fetchProjects() {
    const response = await fetch('/api/projects');
    const data = await response.json();
    return data.map(p => ProjectSchema.parse(p));  // Throws if invalid
}
```

### Detection Strategy

```bash
# Find API responses without model construction
grep -r "return \[{" src/api/ --include="*.py"

# These should use Model(**data).model_dump() instead
```

### Quality Gate

- All API routes use `response_model` parameter
- Callbacks construct response via Pydantic model, not raw dicts
- Frontend validates responses with zod or similar

---

## Lesson 114: Claude Code Subagent Types Are System-Defined

**Date**: 2026-01-30
**Project**: Claude Code Configuration
**Tags**: claude-code, agents, configuration

### Problem

Attempted to register a custom `review` subagent type by adding a file to `~/.claude/agents/review.md`, following the same format as existing registered agents (qa, ba, etc.). The Task tool rejected the new agent type:

```
Agent type 'review' not found. Available agents: Bash, general-purpose,
statusline-setup, Explore, Plan, claude-code-guide, lessons, ba,
design, qa
```

### Root Cause

Claude Code subagent types are **system-defined**, not user-configurable. The `~/.claude/agents/` directory provides prompt content for agents that are already registered in the system, but adding new files does NOT register new `subagent_type` values for the Task tool.

The available subagent types are hardcoded in the Claude Code runtime:
- Built-in: `Bash`, `general-purpose`, `statusline-setup`, `Explore`, `Plan`, `claude-code-guide`
- Custom (pre-registered): `lessons`, `ba`, `design`, `qa`

### Solution

Use an existing agent type with the custom methodology embedded in the prompt:

```python
# Instead of:
Task(subagent_type="review", prompt="Review the project...")

# Use:
Task(subagent_type="qa", prompt="""
You are performing a DEEP CODE REVIEW (not just QA governance check).

Read the full code review methodology from:
/path/to/code-review-agent.md

[Detailed instructions...]
""")
```

### Pattern

For custom agent behaviors:
1. **Create the prompt file** in `~/.claude/agents/` for reference/documentation
2. **Use an existing agent type** that has similar tool access (qa, general-purpose)
3. **Embed the methodology** in the Task prompt, referencing the prompt file

### Detection

```bash
# Check available subagent types by attempting to use one
# Error message lists all valid types

# Files in ~/.claude/agents/ do NOT automatically become subagent types
ls ~/.claude/agents/  # Shows files, but not all are usable as subagent_type
```

### Quality Gate

- Do NOT assume adding files to `~/.claude/agents/` registers new agent types
- Always verify agent type availability before building workflows that depend on it
- Document workarounds when custom agent types are needed

---

## Lesson 115: Fly.io Dev/Prod CI/CD Pipeline Pattern

**Date**: 2026-01-30
**Project**: Little Research Lab
**Tags**: fly.io, deployment, ci-cd, github-actions

### Problem

Needed a dev environment to test changes before promoting to production. The production instance was already live with a custom domain (www.little-research-lab.com), and manual `fly deploy` was error-prone.

### Solution

Create separate Fly.io apps for dev and prod, with GitHub Actions automating the deployment flow:

```
PR → main           Merge to main        Manual trigger
┌──────────┐        ┌──────────┐         ┌──────────┐
│ Quality  │───────▶│ Deploy   │────────▶│ Promote  │
│  Gates   │        │ to Dev   │         │ to Prod  │
└──────────┘        └──────────┘         └──────────┘
```

### Implementation Pattern

**1. Separate Fly.io Apps:**
```
little-research-lab        → Production backend
little-research-lab-web    → Production frontend (custom domain attached)
little-research-lab-dev    → Dev backend
little-research-lab-web-dev → Dev frontend
```

**2. Separate Config Files:**
```
fly.toml           → Production config
fly.dev.toml       → Dev config (smaller VMs, separate volume)
frontend/fly.toml
frontend/fly.dev.toml
```

**3. GitHub Actions Workflows:**
- `.github/workflows/ci.yml` - Quality gates on PR
- `.github/workflows/deploy-dev.yml` - Auto-deploy to dev on merge to main
- `.github/workflows/deploy-prod.yml` - Manual "Promote to Production" with workflow_dispatch

**4. Key Differences for Dev:**
```toml
# fly.dev.toml
app = "little-research-lab-dev"
[[mounts]]
  source = "lrl_data_dev"  # Separate volume!

[[vm]]
  memory = "256mb"  # Smaller for cost savings
```

### Setup Steps

```bash
# 1. Create dev apps
fly apps create little-research-lab-dev --org personal
fly apps create little-research-lab-web-dev --org personal

# 2. Create separate volume for dev database
fly volumes create lrl_data_dev --app little-research-lab-dev --region iad --size 1

# 3. Set secrets
fly secrets set LAB_SECRET_KEY="$(openssl rand -hex 32)" --app little-research-lab-dev

# 4. Generate deploy token and add to GitHub
fly tokens create deploy -x 999999h
gh secret set FLY_API_TOKEN -R owner/repo
```

### Key Insights

1. **Custom domains don't affect deploys** - Deploys target the app name, not the domain. The custom domain is just DNS pointing to the Fly app.

2. **Separate volumes are critical** - Dev must have its own SQLite volume to avoid corrupting production data.

3. **Smoke tests in CI** - Add health checks after deploy to catch startup failures:
```yaml
- name: Check Backend Health
  run: |
    for i in {1..5}; do
      if curl -sf https://little-research-lab-dev.fly.dev/health; then
        exit 0
      fi
      sleep 10
    done
    exit 1
```

4. **Verify dev before prod** - The prod workflow checks dev is healthy before deploying.

### Quality Gate

- [ ] Dev and prod use separate Fly apps and volumes
- [ ] GitHub secret `FLY_API_TOKEN` is set
- [ ] Dev deploys automatically on merge to main
- [ ] Prod requires manual trigger
- [ ] Smoke tests verify services are healthy after deploy

---

## Lesson 116: Multiple Database Files - Verify Which Database the Backend Uses

**Date**: 2026-01-31
**Project**: Little Research Lab
**Category**: Debugging / Local Development

### Problem

When debugging a 500 Internal Server Error caused by invalid UUID data in the database, I fixed the data in `./data/research_lab.db` but the error persisted. The backend was actually using `./data/lrl.db`.

### Root Cause

The project had multiple SQLite database files in the data directory:
- `app.db` (empty/old)
- `research_lab.db` (seed script target)
- `lrl.db` (actual production database)

The backend configuration defaults to `lrl.db` but the seed script and manual fixes targeted `research_lab.db`.

### Symptoms

- Fixed corrupt data but error persisted
- Database queries showed valid data
- Restart didn't help
- Same traceback after "fix"

### Solution

```bash
# 1. List all database files
ls -la ./data/*.db

# 2. Check which file the backend actually uses
grep -r "\.db\|DATABASE" src/app_shell/config.py

# 3. Fix the CORRECT database
sqlite3 ./data/lrl.db "UPDATE content_items SET owner_user_id='...' WHERE owner_user_id='system';"
```

### Prevention

1. **Single source of truth**: Use environment variable `LAB_DATABASE_PATH` consistently
2. **Seed script alignment**: Seed script must target the same database as the backend
3. **Document database location**: Add to CLAUDE.md which database file is used
4. **Clean up old files**: Remove unused database files to avoid confusion

### Quality Gate

- [ ] Only one database file exists in data directory (or clearly documented which is active)
- [ ] Seed script uses same database path as backend
- [ ] Environment variable controls database path in all contexts
- [ ] CLAUDE.md documents the database file location

---

## Lesson 117: D2 Diagram-as-Code for Architecture Documentation

**Date**: 2026-01-31
**Project**: claude-architecture-diagrams
**Category**: Documentation / Tooling

### Context

Evaluated D2 (terrastruct/d2) as an alternative to Mermaid for creating architecture diagrams. D2 is a mature, production-ready tool with 23k+ stars and 3+ years of development.

### Key Learnings

| Topic | Learning |
|-------|----------|
| **Installation** | `brew install d2` - simple, no dependencies |
| **Maturity** | Production-ready (v0.7.1), much more mature than beautiful-mermaid (3 days old) |
| **Default Styling** | Better out-of-box appearance than Mermaid - less configuration needed |
| **Themes** | 0-8 (light), 100-105 (colorblind-friendly), 200-207 (dark) |
| **Live Editing** | `d2 --watch file.d2` opens browser with hot reload |
| **Classes** | Define reusable styles once, apply with `class: stylename` |

### Syntax Gotchas

1. **Avoid markdown blocks in labels** - Use simple quoted strings instead of `|md ... |` blocks which cause parsing errors
2. **External icon URLs may fail** (403 errors) - Use local icons or skip
3. **Nested containers** - Use for logical grouping, works well for architecture layers
4. **Edge labels** - Add after colon: `A -> B: relationship`

### Recommended Patterns

```d2
# Define reusable styles
classes: {
  service: {
    style: {
      fill: "#4CAF50"
      stroke: "#2E7D32"
      font-color: white
      border-radius: 8
    }
  }
}

# Use containers for grouping
layer: Layer Name {
  style.fill: "#E8F5E9"

  service1: Service One {
    class: service
  }
}

# Direction control
direction: right  # or down, left, up
```

### When to Use D2 vs Mermaid

| Use D2 | Use Mermaid |
|--------|-------------|
| Architecture diagrams | Quick sequence diagrams |
| Complex nested layouts | GitHub README inline |
| Custom styling needed | Simple flowcharts |
| Documentation projects | Already in Mermaid ecosystem |

### Quality Gate

- [ ] D2 files in dedicated `diagrams/` or project folder
- [ ] README with rendering instructions
- [ ] Both light and dark theme versions for docs
- [ ] Watch mode used during development

### Evidence

Project: `~/Developer/projects/claude-architecture-diagrams/`
- 6 D2 diagrams documenting Claude Code agent/MCP architecture
- All render successfully to SVG

---

## Lesson 118: Codify Lessons into Reusable Pattern Templates

**Date**: 2026-01-31
**Project**: Claude Code Configuration
**Category**: Process, Knowledge Management, DevOps

### Context

After accumulating 117 lessons in `devlessons.md`, realized the lessons were being referenced but not systematically applied. The DevOps Governor manifest referenced pattern template files that didn't exist, and each new project required manually extracting relevant lessons.

### Problem

Lessons documented in prose form have limited reusability:
- Developers must read through 100+ lessons to find relevant ones
- No copy-paste ready templates for common patterns
- Quality gate configurations recreated from scratch each project
- CI/CD pipelines rebuilt without lessons incorporated
- Manifest referenced patterns that were never created

### Solution

Create reusable pattern templates organized by category, with explicit lesson references:

```
~/.claude/devops/patterns/
├── PATTERNS_INDEX.md              # Usage guide + Top 30 rules
├── quality-gates/
│   ├── python.yaml                # Lessons #4,5,36,51,87,107
│   ├── frontend.yaml              # Lessons #18,38-43,53-57,59,81,85
│   └── fullstack.yaml             # All above + #108,109,113
├── testing/
│   ├── e2e-fixtures.ts.template   # Lessons #44,53-57,60,61
│   └── api-contract-tests.py.template  # Lessons #47,48,108,109,112,113
├── atomic-component/
│   ├── contract.md.template       # Lessons #8,12,79
│   └── component.py.template      # Lessons #8,87,107
├── gitlab-ci/
│   ├── python-fastapi.yml         # Lessons #3,5,115
│   └── nextjs-frontend.yml        # Lessons #18,38-43,53-57,59,81,85,115
├── github-actions/
│   └── python-fastapi.yml         # Mirror of GitLab patterns
└── architecture/
    └── hexagonal-reference.md     # Lessons #4,8,100,103,107
```

### Key Pattern Categories

| Category | Templates | Key Lessons Codified |
|----------|-----------|---------------------|
| Quality Gates | 3 | Determinism checks, evidence artifacts, TDD |
| Testing | 2 | E2E fixtures, API contract validation |
| Atomic Components | 2 | Contract-first, port injection |
| CI/CD | 3 | Progressive deployment, quality gates in pipeline |
| Architecture | 1 | Hexagonal patterns, forbidden imports |

### Template Structure

Each template includes:
- Lesson references with numbers
- Ready-to-use code/configuration
- Prevention checklists
- Evidence requirements
- Agent navigation guides (for CI templates)

### Agent Navigation Benefit

CI templates include predictable directory structure documentation that reduces code search space:

```yaml
# Expected Directory Structure (in nextjs-frontend.yml):
# ├── app/                    # Next.js App Router pages
# ├── components/
# │   ├── ui/                 # shadcn/ui primitives
# │   └── {feature}/          # Feature-specific
# ├── lib/
# │   ├── api/                # API client services
# │   ├── hooks/              # Custom React hooks
# │   └── utils/              # Pure utilities (NO "use client")
```

### Prevention Checklist

- [ ] When adding new lessons, consider if they should become templates
- [ ] Templates must reference specific lesson numbers
- [ ] Include run scripts and evidence artifact paths
- [ ] Create both GitLab and GitHub Actions versions for CI
- [ ] Update PATTERNS_INDEX.md when adding templates
- [ ] Verify manifest references match actual files

### Evidence

- 12 pattern templates created from 117 lessons
- All DevOps manifest pattern references now satisfied
- `PATTERNS_INDEX.md` provides quick lookup by technology

---

## Lesson 119: Fix Upstream Processes, Not Downstream Constraints

**Date**: 2026-01-31
**Project**: Research Lab - Social Media Hub
**Category**: Multi-Agent Workflow, Architecture, Governance

### Context

During implementation of a 30-task Social Media Hub feature using parallel coding agents, experienced repeated friction where the coding agent rejected tasks with "T023 not in manifest.outstanding.tasks". The initial instinct was to relax the coding agent constraint to accept tasks directly from the tasklist file.

### Problem

```
User: "Implement T023"
Coding Agent: "I cannot accept this. T023 not in manifest.outstanding.tasks"
User: "But it's in the tasklist!"
```

The coding agent's BA-only constraint requires all tasks to be in `manifest.outstanding.tasks`. When the BA created a 30-task tasklist but only loaded 5 tasks into the manifest, the remaining 25 tasks were rejected.

**Wrong Solution Proposed:**
```yaml
# DON'T DO THIS
coding_agent:
  task_source: "tasklist"           # Bypasses manifest
  trust_approved_tasklist: true      # Weakens audit trail
```

### Solution

Fix the upstream process (BA task loading) instead of relaxing the downstream constraint:

```yaml
# ~/.claude/agents/ba.md - CORRECT approach

## CRITICAL: Task Loading Protocol (Mandatory)

**The coding agent WILL REJECT tasks not in `manifest.outstanding.tasks`.**
This is by design - manifest is the single source of truth.

### When Creating/Updating Tasklist

After writing `003_tasklist_*.md`, you MUST immediately load ALL tasks:

```yaml
outstanding:
  tasks:
    - id: "T001"
      title: "First task title"
      status: "pending"
      blocked_by: []
      source_file: ".claude/artifacts/003_tasklist_feature_v1.md"
      variant: "feature_name"
    # ... ALL tasks from tasklist, not just first few
```

### Verification Checklist

Before setting `phase: coding`:

- [ ] Count tasks in tasklist file
- [ ] Count tasks in `manifest.outstanding.tasks`
- [ ] **Numbers MUST match**
```

### Why Relaxing Constraints Is Wrong

| Approach | Problem |
|----------|---------|
| Bypass manifest check | Manifest no longer single source of truth |
| Trust tasklist directly | Weakens audit trail for teams |
| Remove BA-only constraint | Security boundary compromised |
| Work around the issue | Root cause remains, will recur |

### The Correct Architecture

```
BA creates tasklist (30 tasks)
       ↓
BA auto-loads ALL 30 tasks into manifest.outstanding.tasks  ← FIX HERE
       ↓
BA sets phase: coding
       ↓
Coding agent checks manifest → T023 found ✓
       ↓
Implementation proceeds smoothly
```

### Drift Feedback Loop

When coding detects drift from spec/tasklist:

1. Coding agent logs to `.claude/evolution/evolution.md`
2. Evolution is fed back to Solution Architect
3. SA updates solution envelope if needed
4. BA updates spec and tasklist
5. BA reloads tasks into manifest
6. Coding continues with corrected spec

**Never relax the coding agent's manifest check** - fix the upstream loading instead.

### Prevention Checklist

- [ ] When a constraint causes friction, ask "what upstream process failed?"
- [ ] BA must verify task count in tasklist matches manifest before setting `phase: coding`
- [ ] Keep downstream security constraints intact (BA-only, manifest-authoritative)
- [ ] Use evolution.md → SA → BA feedback loop for handling drift
- [ ] Document constraint rationale so future maintainers don't remove them

### Evidence

- Updated global BA agent: `~/.claude/agents/ba.md`
- Project lessons: `.claude/evolution/lessons_social_hub.md` (Lessons 9-11)
- Workflow config: `.claude/workflow_config.yaml` confirms `task_source: "manifest"`

---

## Lesson 120: Worktree Consolidation Creates Orphaned Commits

**Date**: 2026-02-02
**Context**: Parallel git worktrees for feature contribution system (fc-submission, fc-voting, fc-moderation, fc-leaderboard)

### Problem

When using parallel git worktrees for feature development, work can be consolidated into one branch while leaving other worktrees with unpushed commits that appear orphaned:

```bash
# Four parallel worktrees created:
research_lab-fc-submission   → Became the "consolidation branch"
research_lab-fc-voting       → Has 2 unpushed commits (T004, T007)
research_lab-fc-moderation   → Has 2 unpushed commits (T005, T006)
research_lab-fc-leaderboard  → Clean

# After merging fc-submission to main:
git log main..origin/fc-voting --oneline
# Returns empty - commits already in main via different path!

# But worktree shows unpushed commits:
cd research_lab-fc-voting && git log origin/fc-voting..HEAD
# 4fa94f9 Implement T007: FeatureVoteRepoSQLite adapter
# 0b6be39 Implement T004: FeatureVoting component
```

The same code exists in main (via fc-submission), but the worktrees show "unpushed" commits because they were merged through a different branch.

### Solution

Before removing worktrees after a consolidated merge:

1. **Check if work is in main** (not just in the worktree's remote branch):
```bash
# Check if the FILES exist in main, not just commit history
ls src/components/feature_voting/  # If exists, work is merged
```

2. **Verify worktree status against main**:
```bash
for wt in research_lab-fc-*; do
  echo "=== $wt ==="
  cd "$wt"
  git diff main --stat | head -5  # Show actual differences from main
done
```

3. **Clean up safely**:
```bash
# Only remove if diff against main is empty or trivial
git worktree remove /path/to/worktree --force
```

### Prevention Checklist

- [ ] When consolidating work, document which worktree contains the final merge
- [ ] After merging consolidated branch, verify all worktrees' changes are in main
- [ ] Don't rely on `git log branch..HEAD` - check file presence instead
- [ ] Consider pushing all worktree branches before consolidation (creates audit trail)
- [ ] Add worktree cleanup to PR merge checklist

---

## Lesson 121: New Routes Need Navigation Menu Items

**Date**: 2026-02-02
**Context**: Feature contribution system deployed with working routes but missing nav links

### Problem

New feature pages worked at their URLs but users couldn't discover them:

```
✓ /features              → Working (public leaderboard)
✓ /features/new          → Working (submission form)
✓ /admin/features/queue  → Working (moderation queue)

✗ TopNavigation.tsx      → No "Feature Ideas" link
✗ admin/layout.tsx       → No "Feature Queue" in sidebar
```

Users could only access features by typing the URL directly. The navigation menus were never updated.

### Solution

Add navigation audit to the feature completion checklist:

```typescript
// TopNavigation.tsx - Add public routes
const navigationConfig: NavItem[] = [
  { label: "Home", href: "/" },
  { label: "About", href: "/about" },
  { label: "Feature Ideas", href: "/features" },  // ADD NEW ROUTES
  // ...
];

// admin/layout.tsx - Add admin routes
<SidebarGroup>
  <SidebarGroupLabel>Community</SidebarGroupLabel>
  <SidebarMenu>
    <SidebarMenuItem>
      <SidebarMenuButton asChild isActive={pathname.startsWith("/admin/features")}>
        <Link href="/admin/features/queue">
          <Lightbulb />
          <span>Feature Queue</span>
        </Link>
      </SidebarMenuButton>
    </SidebarMenuItem>
  </SidebarMenu>
</SidebarGroup>
```

### Navigation Files to Audit

| Route Type | Navigation File | Location |
|------------|-----------------|----------|
| Public pages | `TopNavigation.tsx` | `components/layout/` |
| Admin pages | `layout.tsx` | `app/admin/` |
| Mobile menu | Same files | Check mobile sections too |

### Quality Gate Addition

Add to `005_quality_gates_*.md`:

```markdown
## Navigation Completeness Gate

Before marking feature complete:

- [ ] List all new routes added
- [ ] Verify each route has navigation link
- [ ] Test navigation on desktop AND mobile
- [ ] Verify active state highlighting works
```

### Quick Audit Command

```bash
# Find all page.tsx files (routes)
find app -name "page.tsx" | sort

# Check navigation config
grep -n "href=" components/layout/TopNavigation.tsx
grep -n "href=" app/admin/layout.tsx
```

### Prevention Checklist

- [ ] Add "Navigation link added?" to PR template
- [ ] Include nav audit in E2E tests (can user navigate to new feature?)
- [ ] Update navigation files in same commit as new routes
- [ ] Review navigation during code review, not just functionality

---

## Lesson 122: Manifest Task Status Must Sync on Merge

**Date**: 2026-02-02
**Context**: Feature contribution merged to main but manifest showed 21 tasks as "pending"

### Problem

When code is merged to main (especially from consolidated worktrees), the `manifest.yaml` tasks remain marked as "pending" because the merge operation doesn't update the manifest. This creates a false picture where completed work appears outstanding:

```yaml
# After fc-submission merged to main, manifest still showed:
outstanding:
  tasks:
    - id: "T001"
      status: "pending"  # WRONG - code is merged!
    - id: "T002"
      status: "pending"  # WRONG - code is merged!
    # ... 19 more "pending" tasks that were actually complete
```

**Root cause**: The coding agent handoff focuses on code completion but doesn't enforce manifest updates as part of the merge ceremony. External reviewers check if work is done but don't verify manifest reflects reality.

### Solution

Add manifest sync as a mandatory step in the merge workflow:

**1. Coding Agent Handoff - Add Pre-Merge Checklist:**

```markdown
## Before Creating PR / Merging

- [ ] All tasks for this branch marked `status: "completed"` in manifest
- [ ] Variant status updated (e.g., "parallel_coding" → "complete")
- [ ] `completed` timestamp added to variant
- [ ] `phase` and `phase_note` updated if applicable
- [ ] Manifest committed as part of the final PR
```

**2. Visiting Agent Protocol - Add Manifest Accuracy Check:**

```bash
# Compare merged branches to manifest task statuses
echo "=== MANIFEST ACCURACY CHECK ==="

# Get tasks marked pending
PENDING=$(grep -B1 'status: "pending"' .claude/manifest.yaml | grep "id:" | wc -l)

# Check if related code exists in main
for task_file in src/components/feature_*; do
  if [ -d "$task_file" ]; then
    echo "Code exists: $task_file - verify manifest reflects completion"
  fi
done

echo "Pending tasks in manifest: $PENDING"
echo "If code is merged but tasks show pending, flag as HIGH governance issue"
```

**3. Quality Gate Addition:**

```markdown
## Manifest Sync Gate (G-MANIFEST)

Before merge to main:

- [ ] Count tasks in branch: N
- [ ] Count tasks marked "completed" in manifest: N
- [ ] Numbers MUST match
- [ ] Variant status reflects current state
- [ ] No stale "pending" tasks for merged code
```

### Agent Protocol Updates

**Coding Agent (`~/.claude/agents/coding-agent.md`):**
```markdown
## Merge Ceremony (MANDATORY)

When all tasks for a variant/feature are complete:

1. Update each task: `status: "completed"`, add `completed: "YYYY-MM-DD"`
2. Update variant: `status: "complete"`, add `completed` timestamp
3. Update phase if transitioning (e.g., coding → maintenance)
4. Commit manifest changes WITH the final code changes
5. NEVER merge code without syncing manifest
```

**Visiting Agent (`~/.claude/agents/visit.md`):**
```markdown
## Manifest Accuracy Check (Section 11)

**Priority**: HIGH (governance)

Verify manifest reflects actual codebase state:

1. List all merged feature branches
2. For each, verify corresponding tasks are "completed"
3. Flag discrepancies as BUG-XXX with priority HIGH

**Evidence command:**
```bash
git log --oneline --merges main | head -10
grep 'status: "pending"' .claude/manifest.yaml | wc -l
```
```

### Prevention Checklist

- [ ] Add "Manifest synced?" to PR template
- [ ] Coding agent: include manifest update in merge ceremony
- [ ] Visiting agent: add manifest accuracy to compliance checks
- [ ] Consider CI job: `validate-manifest-sync.sh` comparing git history to task statuses
- [ ] After worktree consolidation, verify ALL worktree tasks marked complete

---

## Lesson 123: Manifest Sync in Parallel Worktree Scenarios

**Date**: 2026-02-02
**Context**: Feature contribution used 4 parallel worktrees (fc-submission, fc-voting, fc-moderation, fc-leaderboard) with consolidation merge pattern

### Problem

Parallel worktrees add manifest sync complexity that Lesson 122 doesn't fully address:

```
Main Worktree (manifest lives here)
    │
    ├── fc-submission (T001, T003, T008, T009, T015, T019)
    ├── fc-voting (T002, T004, T007, T011, T012)
    ├── fc-moderation (T005, T006, T013, T016, T017)
    └── fc-leaderboard (T010, T014)
```

**Issues encountered:**
1. **Ownership ambiguity**: Which worktree updates which tasks in manifest?
2. **Consolidation pattern**: fc-submission merged all work, but tasks from other worktrees stayed "pending"
3. **Timing**: Worktrees were removed before manifest was synced
4. **Conflict potential**: Multiple agents could try updating manifest simultaneously

### Solution

**1. Designate Manifest Owner in Worktree Config:**

```yaml
# .claude/manifest.yaml
worktree_governance:
  max_parallel: 4
  manifest_owner: "main"  # Only main worktree updates manifest
  consolidation_branch: "fc-submission"  # This branch merges all others

active_worktrees:
  - name: "fc-submission"
    is_consolidator: true  # Responsible for final manifest sync
    owns_tasks: ["T001", "T003", "T008", "T009", "T015", "T019"]
    absorbs_from: ["fc-voting", "fc-moderation", "fc-leaderboard"]

  - name: "fc-voting"
    is_consolidator: false
    owns_tasks: ["T002", "T004", "T007", "T011", "T012"]
    manifest_deferred: true  # Consolidator will update these
```

**2. Consolidation Merge Protocol:**

```markdown
## When Consolidating Multiple Worktrees

### Before Merging Consolidated Branch to Main:

1. List ALL tasks from ALL absorbed worktrees
2. Mark EVERY task as `status: "completed"` (not just your own)
3. Update variant status to "complete"
4. Add completion timestamps

### Manifest Update Checklist:
- [ ] Tasks from fc-submission: marked complete
- [ ] Tasks from fc-voting: marked complete
- [ ] Tasks from fc-moderation: marked complete
- [ ] Tasks from fc-leaderboard: marked complete
- [ ] Variant status: "complete"
- [ ] Phase updated if needed
- [ ] Commit manifest WITH merge commit
```

**3. Worktree Cleanup Sequence (ORDER MATTERS):**

```bash
# CORRECT ORDER:
1. Merge consolidation branch to main
2. Update manifest (mark ALL tasks complete)
3. Commit and push manifest
4. THEN remove worktrees

# WRONG ORDER (what we did):
1. Merge consolidation branch to main
2. Remove worktrees  # Too early!
3. Forget to update manifest  # Tasks still "pending"
```

**4. Parallel Manifest Lock Pattern:**

```markdown
## Manifest Locking for Parallel Work

To prevent conflicts:

1. Feature worktrees NEVER edit manifest directly
2. Only main worktree (or designated consolidator) updates manifest
3. Worktree agents report completion via handoff envelope, not manifest edit
4. Consolidator aggregates all completions into single manifest update
```

**5. Handoff Envelope for Worktree Completion:**

```yaml
# .claude/handoff/fc-voting_completion.yaml
worktree: "fc-voting"
branch: "fc-voting"
completed_tasks:
  - id: "T002"
    title: "Create FeatureRequest and FeatureVote Domain Entities"
    evidence: ".claude/evidence/T002_social_entities_completion.md"
  - id: "T004"
    title: "Create FeatureVoting Component"
    evidence: ".claude/evidence/T004_completion_summary.md"
  # ...
ready_for_consolidation: true
timestamp: "2026-02-02T15:00:00Z"

# Consolidator reads these and updates manifest accordingly
```

### Visiting Agent: Parallel Worktree Audit

Add to external review protocol:

```bash
# Check for orphaned worktree tasks
echo "=== PARALLEL WORKTREE AUDIT ==="

# 1. Check if worktrees still exist
git worktree list

# 2. If worktrees removed, verify their tasks are complete
if [ ! -d "../research_lab-fc-voting" ]; then
  echo "fc-voting worktree removed - checking task status..."
  grep -A 2 "T002\|T004\|T007" .claude/manifest.yaml | grep "status"
fi

# 3. Flag if removed worktree has pending tasks
PENDING_FROM_REMOVED=$(grep -B 5 'status: "pending"' .claude/manifest.yaml | grep "fc-voting\|fc-moderation" | wc -l)
if [ "$PENDING_FROM_REMOVED" -gt 0 ]; then
  echo "FAIL: Removed worktrees have pending tasks in manifest"
fi
```

### Prevention Checklist

- [ ] Designate `manifest_owner` and `consolidation_branch` in worktree config
- [ ] Consolidator marks ALL absorbed tasks complete, not just their own
- [ ] Never remove worktrees until manifest is synced and pushed
- [ ] Use handoff envelopes for worktree completion reporting
- [ ] Visiting agent: audit for orphaned worktree tasks
- [ ] Add manifest sync to worktree removal script

### Evidence

- research_lab (2026-02-02): 21 tasks left "pending" after fc-submission merge
- Root cause: Consolidation merged code but didn't update manifest for absorbed worktrees
- Fixed by: Manual manifest update marking all T001-T021 as complete

---

### Lesson 56: Extracting Icons from PDFs with PyMuPDF and Precise Cropping

**What happened (product_content, 2026-02-03):**

When creating presentation templates matching a NotebookLM-generated PDF style, we needed to extract individual icons and diagrams from the PDF for reuse. Initial attempts to crop icons resulted in partial captures - getting text headers instead of icons, or only corners of the intended graphics. The challenge was that PDF embedded images don't always align with visual elements, and icon positions vary per slide layout.

**The fix:**

Use PyMuPDF (fitz) to render high-resolution page images, then use Pillow to crop specific regions with iteratively refined coordinates:

```python
import fitz  # PyMuPDF
from PIL import Image

# Render at 2x scale for high-res extraction
doc = fitz.open("presentation.pdf")
for page_num, page in enumerate(doc):
    mat = fitz.Matrix(2.0, 2.0)  # 2x scale
    pix = page.get_pixmap(matrix=mat)
    pix.save(f"hires_pages/slide_{page_num:02d}.png")

# Then crop specific regions (coordinates found through iteration)
CROPS = {
    "slide_02.png": [
        ("icon_challenge.png", (50, 280, 480, 800)),  # (left, upper, right, lower)
        ("icon_solution.png", (1020, 280, 1500, 800)),
    ],
}

for slide, crops in CROPS.items():
    img = Image.open(f"hires_pages/{slide}")
    for name, bbox in crops:
        cropped = img.crop(bbox)
        cropped.save(f"cropped/{name}")
```

**Key insight:** Icon positions must be found empirically - render the full slide, view it, estimate coordinates, crop, check result, adjust. Budget 3-5 iterations per icon to get clean crops without adjacent text or partial graphics.

### Future Checklist:
- [ ] Render PDF pages at 2x or higher scale before cropping (2752x1536 for 16:9 slides)
- [ ] Create a crop definition dict mapping slide files to (icon_name, bbox) tuples
- [ ] Verify each crop visually - icons are often positioned differently than expected
- [ ] For HTML templates, embed images as base64 data URIs to avoid path issues with file:// protocol
- [ ] Keep both hires renders and cropped icons - may need to re-crop with different coordinates

---

## Lesson 124: Grep Patterns Must Match All Heading Variations

**Date**: 2026-02-04
**Context**: Claude Agent Framework - /learn command reporting wrong lesson count

### Problem

The `/learn` command reported only 60 lessons when there were actually 151. The grep pattern `^### Lesson` only matched lessons with exactly 3 hashes, but lessons used varying heading levels:

```markdown
## Lesson 113: ...   (2 hashes - newer format)
### Lesson: ...      (3 hashes - older format)
#### Lesson 35a: ... (4 hashes - sub-lessons)
```

This caused the lesson count to be wildly inaccurate, and new lessons would get incorrect numbers.

### Solution

Use extended regex with `+` quantifier to match one or more `#` characters:

```bash
# OLD - only matches ### (3 hashes)
grep -c "^### Lesson" devlessons.md  # Returns 60

# NEW - matches ##, ###, #### etc.
grep -cE "^##+ Lesson" devlessons.md  # Returns 151
```

For finding the highest numbered lesson (to determine next number):

```bash
grep -oE "Lesson [0-9]+" devlessons.md | sed 's/Lesson //' | sort -n | tail -1
# Returns: 123 (so next lesson is 124)
```

### Future Checklist
- [ ] When counting markdown sections, use `^##+` pattern to match all heading levels
- [ ] Test grep patterns against actual file content before deploying
- [ ] For numbered sequences, extract and sort numerically rather than counting occurrences
- [ ] Document format variations in files that evolved over time

---

## Lesson 125: Phased Testing Strategy for Sandbox Infrastructure

**Date**: 2026-02-04
**Context**: Agent Sandbox Infrastructure - isolated Docker containers for AI coding agents

### Problem

When building sandbox infrastructure that isolates AI agents from sensitive files (like `~/.claude/agents/`), testing requires a careful phased approach. Running untested sandbox code against real projects risks:

1. Accidental access to agent prompts (contamination)
2. Unintended file modifications
3. Credential leakage via environment variables
4. Network exfiltration of sensitive data

Simply writing unit tests isn't enough - you need integration tests that verify actual Docker container isolation.

### Solution

Implement a 4-phase testing strategy with dedicated test scripts:

**Phase 1: Dry Run** - Unit tests only (no Docker)
```bash
pytest tests/unit -v  # 164 tests, 82% coverage
```

**Phase 2: Safe Project Test** - Throwaway repo
```python
# scripts/phase2_safe_project_test.py
# Creates temp project, spawns container, verifies:
# - Container can read/write workspace
# - Container CANNOT access ~/.claude/
# - No credential leakage
# - Quality gates run inside container
# - Baseline verification works
```

**Phase 3: Real Project Read-Only** - Your code, but protected
```python
# scripts/phase3_readonly_project_test.py
# Mounts real project with :ro flag
# - Verifies write attempts FAIL
# - Hashes ALL files before/after
# - Runs quality gates (may fail due to cache dirs)
# - Confirms zero file modifications
```

**Phase 4: Real Project Read-Write** - Full integration (manual review)

**Key Contamination Prevention Tests:**
```python
def test_forbidden_mount_path_rejected():
    """~/.claude/agents/ cannot be mounted."""

def test_symlink_to_forbidden_path_rejected():
    """Symlinks to forbidden paths also blocked."""

def test_container_cannot_access_host_claude_directory():
    """Container cannot read host ~/.claude/ via any mechanism."""

def test_environment_does_not_contain_real_credentials():
    """No ANTHROPIC_API_KEY, GITHUB_TOKEN, etc."""

def test_network_none_prevents_exfiltration():
    """Air-gapped containers cannot phone home."""
```

### Future Checklist
- [ ] Always test sandbox infrastructure in phases (safe → read-only → read-write)
- [ ] Hash ALL project files before/after container runs to detect modifications
- [ ] Test symlink attacks against forbidden path checks (use `path.resolve()`)
- [ ] Verify credential isolation by checking container env vars
- [ ] Mount real projects read-only first before allowing writes
- [ ] Keep test container running with `--keep-container` flag for debugging

---

## Lesson 126: Governance Bypass via Reactive Mode After Context Compress

**Date**: 2026-02-06
**Project**: Little Research Lab
**Context**: Production issue triage - newsletter signup broken, inbox validation error
**Tags**: governance, process, agent-workflow, context-compress

### Problem

After a context compress, session resumed with urgent production issues. Instead of following established governance workflow, I entered reactive "fix it now" mode:

1. **Skipped manifest.yaml read** - Failed to re-anchor after context loss
2. **Bypassed BA workflow** - Modified code directly instead of creating spec + tasklist
3. **Coded without agents** - Used internal Edit/Write tools instead of back and front
4. **Modified multiple files atomically** - Changed sqlite_db.py, admin_newsletter.py, newsletter/page.tsx, AND created migration 023_fix_sent_emails_schema.sql in single session
5. **No governance checkpoints** - Skipped quality gates, no evidence artifacts, didn't update manifest.yaml

**Root cause**: Urgency triggered exception mindset ("this is different, rules don't apply"). Post-compress context loss meant governance rules weren't in working memory. Pre-compress session momentum continued without re-anchoring.

### Why This Violates Governance

The exclusive permissions exist **precisely for urgent situations**:

- **Coding agents maintain determinism** - TDD, hexagonal architecture, component contracts
- **BA maintains traceability** - Specs and tasklists connect changes to business rationale
- **Quality gates prevent regressions** - Catch issues before production impact
- **Evidence artifacts create audit trail** - Future sessions understand why code exists

Bypassing governance to "just fix urgent issue" creates:
1. **Drift uncovered later** - Side effects discovered only in production
2. **Lost traceability** - Future developers don't know why code is this way
3. **Governance precedent problem** - Creates pattern that governance is optional when convenient
4. **Accumulated technical debt** - Undocumented fixes compound into unmaintainable code

### The Fix

**After context compress, governance becomes MORE critical, not less:**

```
RESTART AFTER CONTEXT COMPRESS:
1. Read manifest.yaml        ← Current state
2. Create spec/tasklist      ← Formalize even urgent fixes
3. Invoke coding agents      ← Never bypass exclusive permissions
4. Quality gates pass        ← Verify no regressions
5. Update manifest + evidence ← Create audit trail
```

**Urgency doesn't override governance - it makes governance more important.**

### Detection: Quality Gate to Prevent Recurrence

```yaml
governance_sync:
  - name: "Manifest synchronized with recent changes"
    command: "git diff HEAD~10 -- '.claude/manifest.yaml' | grep -c 'updated_at:' || echo 0"
    expected_min: "1 (at least one manifest update in last 10 commits)"
    lesson_ref: 126

  - name: "Code changes have task IDs"
    command: "git log --oneline -15 -- 'src/**/*.py' 'frontend/**/*.tsx' | grep -cE 'TASK|SPEC|BUG-|IMPROVE-|EV-'"
    expected_min: "number of commits modifying code"
    lesson_ref: 126
```

### Restart Protocol (After Context Compress)

**MANDATORY CHECKLIST before any coding decision:**

```markdown
# RESTART CHECKLIST

[ ] 1. Read `.claude/manifest.yaml` FIRST
[ ] 2. Read `.claude/session_state.md` (if exists)
[ ] 3. Check outstanding.remediation - handle BUG-XXX first
[ ] 4. Check outstanding.tasks - continue pending work
[ ] 5. Re-read system prompt - Governance rules for your role
[ ] 6. Verify current git branch - Not on merge commit
[ ] 7. Run quality gates - Baseline before new work

ONLY AFTER 1-7 can you proceed with new work.

For urgent issues found in step 3:
  - Create tasklist entry (even if "URGENT")
  - DO NOT code directly
  - Invoke appropriate agent
  - Wait for handoff
```

### Future Checklist

- [ ] After context compress: Read manifest.yaml FIRST
- [ ] For urgent fixes: Create spec/tasklist - takes 5 min, prevents 5 hours debugging
- [ ] Invoke agents, don't bypass them - Agents exist because shortcuts don't scale
- [ ] Quality gates are non-negotiable - Run after every fix
- [ ] Update evidence - Each change needs .claude/evidence/ artifacts
- [ ] If you bypass governance: Document explicitly in decisions.md with rationale

### Related Lessons

- Lesson #7: Process & Governance
- Lesson #25: Solution Designer → BA → Coding Agent Workflow
- Lesson #31: Governance Drift via Atomic Component Drift
- Lesson #101: Parallel Agent Execution for Large Feature Implementation
- Lesson #102: Solution Designer → BA → Coding Agent Pipeline

---

## Lesson 127: Content Publishing via API (Research Lab)

**Date**: 2026-02-06
**Project**: research_lab
**Category**: Content API, TipTap, SSR
**Severity**: HIGH

### Problem

When publishing articles programmatically via the content API, multiple issues caused content to not render:

1. **Wrong block_type**: Used `block_type: "tiptap"` but frontend expects `block_type: "markdown"`
2. **DOMPurify SSR failure**: `dompurify` is browser-only, fails on server-side rendering
3. **Duplicate extensions**: Adding `Link` extension when `StarterKit` already includes it

### Root Cause

The content storage format uses:
```json
{
  "blocks": [{
    "block_type": "markdown",  // NOT "tiptap"!
    "data_json": {
      "tiptap": { "type": "doc", "content": [...] }
    }
  }]
}
```

The admin frontend (`app/admin/content/[id]/page.tsx:108`) explicitly looks for `data_json.tiptap` inside a `markdown` block type.

### Fixes Applied

1. **block_type**: Always use `"markdown"` for TipTap content
2. **DOMPurify**: Replaced with `isomorphic-dompurify` for SSR compatibility
3. **Extensions**: Removed duplicate `Link.configure()` from extensions array

### Content Publishing Workflow

```python
# Correct format for API content creation
payload = {
    "type": "post",
    "title": "Article Title",
    "slug": "article-slug",
    "summary": "Short description",
    "blocks": [{
        "block_type": "markdown",  # MUST be "markdown"
        "data_json": {
            "tiptap": {
                "type": "doc",
                "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": "..."}]},
                    {"type": "heading", "attrs": {"level": 2}, "content": [...]},
                    # etc.
                ]
            }
        }
    }],
    "access_rule_json": "{}",
    "teaser_visible": True
}
```

### TipTap Node Types Supported

| Node Type | Usage |
|-----------|-------|
| `paragraph` | Body text |
| `heading` | `attrs: {level: 2}` for h2, etc. |
| `bulletList` | Contains `listItem` nodes |
| `orderedList` | Contains `listItem` nodes |
| `codeBlock` | Standard code blocks |
| `horizontalRule` | Dividers |
| `blockquote` | Quotes |

### Text Marks

```json
{"type": "text", "marks": [{"type": "bold"}], "text": "bold text"}
{"type": "text", "marks": [{"type": "italic"}], "text": "italic text"}
{"type": "text", "marks": [{"type": "link", "attrs": {"href": "..."}}], "text": "link"}
```

### Quality Gate

```bash
# After publishing via API, verify rendering
curl -s "https://example.com/p/SLUG" | grep -o "__next_error__" && echo "FAIL: Rendering error"
curl -s "https://example.com/p/SLUG" | grep -o "Expected text from article" || echo "FAIL: Content not visible"
```

### Related Files

- `frontend/components/content/block-renderer.tsx` - Routes block types
- `frontend/components/content/TipTapContentRenderer.tsx` - Renders TipTap JSON
- `frontend/app/admin/content/[id]/page.tsx` - Admin editor expectations

### Key Insight

The naming is confusing: `block_type: "markdown"` actually contains TipTap JSON in `data_json.tiptap`. This is legacy naming that should not be changed without migration.
