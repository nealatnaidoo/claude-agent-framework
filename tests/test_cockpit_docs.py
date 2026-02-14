"""Tests for cockpit documentation collector."""

import json
from pathlib import Path

import pytest

from claude_cli.cockpit.docs_collector import (
    _parse_agents,
    _parse_coding_tips,
    _parse_commands,
    _parse_governance,
    _parse_patterns_index,
    _parse_tools_registry,
    collect_docs_data,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def framework_dir(tmp_path):
    """Create a minimal framework structure with docs sources."""
    # tools/registry.yaml
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    (tools_dir / "registry.yaml").write_text(
        """\
schema_version: "1.0"
scripts:
  validate_agents:
    path: "scripts/validate_agents.py"
    description: "Validate agent prompts"
    usage: "python scripts/validate_agents.py [agent.md]"
    used_by: [ops, qa]
  version_tracker:
    path: "scripts/version_tracker.py"
    description: "Track version changes"
    usage: "python scripts/version_tracker.py scan"
    used_by: [ops]

packages:
  db-harness:
    name: "Database Propagation Harness"
    version: "1.0.0"
    description: "Database propagation with PII masking"
    commands:
      propagate: "Propagate data"
      drift: "Detect schema drift"

planned:
  secret-rotate:
    category: package
    purpose: "Credential rotation automation"
    status: planned
"""
    )

    # agents/*.md
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    (agents_dir / "ba.md").write_text(
        '---\nname: ba\ndescription: "Business analyst agent"\nmodel: opus\n---\n\nContent here.\n'
    )
    (agents_dir / "back.md").write_text(
        '---\nname: back\ndescription: "Backend coding agent"\nmodel: opus\n---\n\nContent here.\n'
    )
    (agents_dir / "ops.md").write_text(
        '---\nname: ops\ndescription: "DevOps operations"\nmodel: opus\n---\n\nContent here.\n'
    )
    # Non-md file should be skipped
    (agents_dir / "README.txt").write_text("Not an agent")

    # CLAUDE.md
    (tmp_path / "CLAUDE.md").write_text(
        """\
# Claude Code Global Instructions

## Prime Directive (Non-Negotiable)

> **Every change must be task-scoped, atomic, deterministic, hexagonal, and evidenced.**

## Agent Routing

### Micro Agents (Project Level)

| Agent | Model | When to Use | Exclusive Permission |
|-------|-------|-------------|---------------------|
| `ba` | opus | Create spec | - |
| `back` | opus | Python backend | **Write backend code** |
| `front` | opus | React frontend | **Write frontend code** |
| `persona` | opus | Define journeys | **Define user journeys** |

## Agent Lifecycle

```
init -> persona -> lessons
                     |
                  design -> ba -> coding -> qa -> review
```

## Available Commands

| Command | Purpose |
|---------|---------|
| `/review-project` | Prime Directive compliance check |
| `/commit` | Create git commit |
| `/status` | Display system status |

## Governance Essentials

- **Manifest as Universal Entry Gate**: ALL agents read manifest FIRST
- **Phase enforcement**: Hooks block agents from running in wrong phase
- **Never overwrite artifacts**: Always create new versions (v1 -> v2)
"""
    )

    # patterns/PATTERNS_INDEX.md
    patterns_dir = tmp_path / "patterns"
    patterns_dir.mkdir()
    (patterns_dir / "PATTERNS_INDEX.md").write_text(
        """\
# Best Practice Pattern Templates Index

## Pattern Categories

### 1. Quality Gates (`quality-gates/`)

| Template | Purpose | Key Lessons |
|----------|---------|-------------|
| `python.yaml` | Python project quality gates | #4, #5 |
| `frontend.yaml` | Next.js/React quality gates | #18, #38 |

### 2. Testing Patterns (`testing/`)

| Template | Purpose | Key Lessons |
|----------|---------|-------------|
| `e2e-fixtures.ts.template` | Playwright E2E test fixtures | #44, #53 |
| `api-contract-tests.py.template` | API contract validation | #47, #48 |
"""
    )

    # knowledge/coding_standards.md
    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir()
    (knowledge_dir / "coding_standards.md").write_text(
        """\
# Coding Standards Quick Reference

## Verification Checkpoints (Non-Negotiable)

**After ANY file edit (Edit/Write tool), run verification:**

**Self-Audit Questions:**
- Am I following TDD (tests before implementation)?
- Am I staying within task scope?
- Are my changes hexagonal?

**Strict Prohibitions:**
- NEVER skip the verification checkpoint
- NEVER mark a task done without evidence artifacts
- NEVER continue past 40 turns without fresh conversation
"""
    )

    return tmp_path


# ---------------------------------------------------------------------------
# TestParseToolsRegistry
# ---------------------------------------------------------------------------


class TestParseToolsRegistry:
    def test_parses_scripts(self, framework_dir):
        result = _parse_tools_registry(framework_dir / "tools" / "registry.yaml")
        assert len(result["scripts"]) == 2
        names = {s["name"] for s in result["scripts"]}
        assert "validate_agents" in names
        assert "version_tracker" in names
        # Check fields
        va = next(s for s in result["scripts"] if s["name"] == "validate_agents")
        assert va["description"] == "Validate agent prompts"
        assert va["used_by"] == ["ops", "qa"]

    def test_parses_packages(self, framework_dir):
        result = _parse_tools_registry(framework_dir / "tools" / "registry.yaml")
        assert len(result["packages"]) == 1
        pkg = result["packages"][0]
        assert pkg["name"] == "Database Propagation Harness"
        assert pkg["version"] == "1.0.0"
        assert "propagate" in pkg["commands"]
        assert "drift" in pkg["commands"]

    def test_parses_planned(self, framework_dir):
        result = _parse_tools_registry(framework_dir / "tools" / "registry.yaml")
        assert len(result["planned"]) == 1
        assert result["planned"][0]["name"] == "secret-rotate"
        assert result["planned"][0]["status"] == "planned"

    def test_missing_file(self, tmp_path):
        result = _parse_tools_registry(tmp_path / "nonexistent.yaml")
        assert result == {"scripts": [], "packages": [], "planned": []}

    def test_empty_yaml(self, tmp_path):
        f = tmp_path / "empty.yaml"
        f.write_text("")
        result = _parse_tools_registry(f)
        assert result == {"scripts": [], "packages": [], "planned": []}


# ---------------------------------------------------------------------------
# TestParseAgents
# ---------------------------------------------------------------------------


class TestParseAgents:
    def test_extracts_frontmatter(self, framework_dir):
        agents = _parse_agents(framework_dir / "agents")
        assert len(agents) == 3
        names = {a["name"] for a in agents}
        assert names == {"ba", "back", "ops"}

    def test_agent_fields(self, framework_dir):
        agents = _parse_agents(framework_dir / "agents")
        back = next(a for a in agents if a["name"] == "back")
        assert back["model"] == "opus"
        assert back["scope"] == "micro"
        assert back["exclusive_permission"] == "Write backend code"

    def test_macro_scope(self, framework_dir):
        agents = _parse_agents(framework_dir / "agents")
        ops = next(a for a in agents if a["name"] == "ops")
        assert ops["scope"] == "macro"
        assert ops["exclusive_permission"] == "Execute deployments"

    def test_missing_fields(self, tmp_path):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        (agents_dir / "minimal.md").write_text("---\nname: minimal\n---\n\nBody.\n")
        agents = _parse_agents(agents_dir)
        assert len(agents) == 1
        assert agents[0]["name"] == "minimal"
        assert agents[0]["model"] == ""

    def test_skips_non_md(self, framework_dir):
        # README.txt exists in fixture but should not be parsed
        agents = _parse_agents(framework_dir / "agents")
        names = {a["name"] for a in agents}
        assert "README" not in names

    def test_empty_dir(self, tmp_path):
        d = tmp_path / "agents"
        d.mkdir()
        assert _parse_agents(d) == []

    def test_missing_dir(self, tmp_path):
        assert _parse_agents(tmp_path / "nonexistent") == []


# ---------------------------------------------------------------------------
# TestParseCommands
# ---------------------------------------------------------------------------


class TestParseCommands:
    def test_extracts_table(self, framework_dir):
        commands = _parse_commands(framework_dir / "CLAUDE.md")
        assert len(commands) == 3
        names = {c["name"] for c in commands}
        assert "/review-project" in names
        assert "/commit" in names
        assert "/status" in names

    def test_command_descriptions(self, framework_dir):
        commands = _parse_commands(framework_dir / "CLAUDE.md")
        review = next(c for c in commands if c["name"] == "/review-project")
        assert "compliance" in review["description"].lower()

    def test_missing_section(self, tmp_path):
        f = tmp_path / "CLAUDE.md"
        f.write_text("# No commands here\n\nJust some text.\n")
        assert _parse_commands(f) == []

    def test_missing_file(self, tmp_path):
        assert _parse_commands(tmp_path / "nonexistent.md") == []


# ---------------------------------------------------------------------------
# TestParsePatternsIndex
# ---------------------------------------------------------------------------


class TestParsePatternsIndex:
    def test_extracts_categories(self, framework_dir):
        patterns = _parse_patterns_index(
            framework_dir / "patterns" / "PATTERNS_INDEX.md"
        )
        assert len(patterns) == 2
        cats = {p["category"] for p in patterns}
        assert "Quality Gates" in cats
        assert "Testing Patterns" in cats

    def test_template_contents(self, framework_dir):
        patterns = _parse_patterns_index(
            framework_dir / "patterns" / "PATTERNS_INDEX.md"
        )
        qg = next(p for p in patterns if p["category"] == "Quality Gates")
        assert len(qg["templates"]) == 2
        names = {t["name"] for t in qg["templates"]}
        assert "python.yaml" in names

    def test_missing_file(self, tmp_path):
        assert _parse_patterns_index(tmp_path / "nonexistent.md") == []


# ---------------------------------------------------------------------------
# TestParseCodingTips
# ---------------------------------------------------------------------------


class TestParseCodingTips:
    def test_extracts_self_audit(self, framework_dir):
        tips = _parse_coding_tips(framework_dir / "knowledge" / "coding_standards.md")
        audit = next(
            (t for t in tips if t["category"] == "Self-Audit Questions"), None
        )
        assert audit is not None
        assert any("TDD" in item for item in audit["items"])

    def test_extracts_prohibitions(self, framework_dir):
        tips = _parse_coding_tips(framework_dir / "knowledge" / "coding_standards.md")
        prohib = next(
            (t for t in tips if t["category"] == "Strict Prohibitions"), None
        )
        assert prohib is not None
        assert len(prohib["items"]) == 3

    def test_missing_file(self, tmp_path):
        assert _parse_coding_tips(tmp_path / "nonexistent.md") == []


# ---------------------------------------------------------------------------
# TestParseGovernance
# ---------------------------------------------------------------------------


class TestParseGovernance:
    def test_extracts_prime_directive(self, framework_dir):
        gov = _parse_governance(framework_dir / "CLAUDE.md")
        assert "task-scoped" in gov["prime_directive"]
        assert "evidenced" in gov["prime_directive"]

    def test_extracts_permissions(self, framework_dir):
        gov = _parse_governance(framework_dir / "CLAUDE.md")
        assert len(gov["permissions"]) >= 2
        agents = {p["agent"] for p in gov["permissions"]}
        assert "back" in agents
        assert "front" in agents

    def test_extracts_lifecycle(self, framework_dir):
        gov = _parse_governance(framework_dir / "CLAUDE.md")
        assert "init" in gov["lifecycle"]
        assert "persona" in gov["lifecycle"]

    def test_extracts_rules(self, framework_dir):
        gov = _parse_governance(framework_dir / "CLAUDE.md")
        assert len(gov["rules"]) >= 2
        sections = {r["section"] for r in gov["rules"]}
        assert "Manifest as Universal Entry Gate" in sections

    def test_missing_file(self, tmp_path):
        gov = _parse_governance(tmp_path / "nonexistent.md")
        assert gov["prime_directive"] == ""
        assert gov["permissions"] == []
        assert gov["lifecycle"] == ""
        assert gov["rules"] == []


# ---------------------------------------------------------------------------
# TestCollectDocsData
# ---------------------------------------------------------------------------


class TestCollectDocsData:
    def test_complete_dict_structure(self, framework_dir):
        data = collect_docs_data(framework_dir)
        assert "tools" in data
        assert "agents" in data
        assert "commands" in data
        assert "patterns" in data
        assert "coding_tips" in data
        assert "governance" in data

    def test_all_keys_with_missing_sources(self, tmp_path):
        # Empty framework root - all parsers should return defaults
        data = collect_docs_data(tmp_path)
        assert data["tools"] == {"scripts": [], "packages": [], "planned": []}
        assert data["agents"] == []
        assert data["commands"] == []
        assert data["patterns"] == []
        assert data["coding_tips"] == []
        assert data["governance"]["prime_directive"] == ""

    def test_json_serializable(self, framework_dir):
        data = collect_docs_data(framework_dir)
        # Must not raise
        json_str = json.dumps(data, indent=2, default=str)
        assert isinstance(json_str, str)
        # Round-trip
        parsed = json.loads(json_str)
        assert parsed["tools"]["scripts"][0]["name"] == "validate_agents"

    def test_custom_framework_root(self, framework_dir):
        data = collect_docs_data(framework_root=framework_dir)
        assert len(data["agents"]) == 3
        assert len(data["commands"]) == 3


# ---------------------------------------------------------------------------
# TestTemplateIntegration
# ---------------------------------------------------------------------------


class TestTemplateIntegration:
    """Verify templates work with docs_data injection."""

    def _render_project(self, framework_dir):
        """Helper to render project HTML with docs data."""
        from claude_cli.cockpit.docs_collector import collect_docs_data
        from claude_cli.cockpit.generator import collect_data, render_html

        # Create a minimal project
        claude_dir = framework_dir / "test-project" / ".claude"
        claude_dir.mkdir(parents=True)
        (claude_dir / "manifest.yaml").write_text(
            'project_slug: "test"\nproject_name: "Test"\nphase: "coding"\n'
        )
        project_root = framework_dir / "test-project"
        data = collect_data(project_root)
        return render_html(data), collect_docs_data(framework_dir)

    def test_project_html_has_tab_bar(self):
        """Verify project template has tab navigation."""
        from claude_cli.cockpit.generator import render_html

        data = {
            "project_name": "Test",
            "generated_at": "2026-01-01",
            "phase": "coding",
            "tasks": {"pending": 0, "in_progress": 0, "completed": 0, "blocked": 0},
            "quality_gates": None,
            "remediation": {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0},
            "outbox": {"pending": 0, "active": 0, "completed": 0, "rejected": 0},
            "commits": [],
            "artifacts": {},
        }
        html = render_html(data)
        assert "tab-bar" in html
        assert "switchTab" in html
        assert "tab-dashboard" in html
        assert "tab-reference" in html
        assert "tab-patterns" in html
        assert "tab-governance" in html

    def test_project_html_dashboard_tab_has_existing_sections(self):
        """Existing dashboard sections must still be present."""
        from claude_cli.cockpit.generator import render_html

        data = {
            "project_name": "Test",
            "generated_at": "2026-01-01",
            "phase": "coding",
            "tasks": {"pending": 0, "in_progress": 0, "completed": 0, "blocked": 0},
            "quality_gates": None,
            "remediation": {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0},
            "outbox": {"pending": 0, "active": 0, "completed": 0, "rejected": 0},
            "commits": [],
            "artifacts": {},
        }
        html = render_html(data)
        assert "Task Progress" in html
        assert "Quality Gates" in html
        assert "Remediation" in html
        assert "Recent Commits" in html

    def test_project_html_docs_data_present(self):
        """Docs data placeholder must be present in template."""
        from claude_cli.cockpit.generator import render_html

        data = {
            "project_name": "Test",
            "generated_at": "2026-01-01",
            "phase": "coding",
            "tasks": {"pending": 0, "in_progress": 0, "completed": 0, "blocked": 0},
            "quality_gates": None,
            "remediation": {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0},
            "outbox": {"pending": 0, "active": 0, "completed": 0, "rejected": 0},
            "commits": [],
            "artifacts": {},
        }
        html = render_html(data)
        assert "DOCS" in html

    def test_portfolio_html_has_tab_bar(self):
        """Verify portfolio template has tab navigation."""
        from claude_cli.cockpit.portfolio import render_portfolio_html

        data = {
            "portfolio_name": "Test Portfolio",
            "generated_at": "2026-01-01",
            "project_count": 0,
            "projects": [],
            "totals": {"tasks_pending": 0, "tasks_completed": 0, "tasks_in_progress": 0, "tasks_blocked": 0},
            "phase_distribution": {},
        }
        html = render_portfolio_html(data)
        assert "tab-bar" in html
        assert "switchTab" in html
        assert "tab-dashboard" in html

    def test_existing_cockpit_data_unaffected(self):
        """Regression: COCKPIT_DATA JSON embedding must still work."""
        from claude_cli.cockpit.generator import render_html

        data = {
            "project_name": "Regression Test",
            "project_slug": "regression-test",
            "generated_at": "2026-01-01",
            "phase": "coding",
            "tasks": {"pending": 1, "in_progress": 0, "completed": 2, "blocked": 0},
            "quality_gates": None,
            "remediation": {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0},
            "outbox": {"pending": 0, "active": 0, "completed": 0, "rejected": 0},
            "commits": [],
            "artifacts": {},
        }
        html = render_html(data)
        assert "COCKPIT_DATA" in html
        # Extract and parse JSON - must still work
        start = html.index("COCKPIT_DATA = ") + len("COCKPIT_DATA = ")
        end = html.index(";\n", start)
        embedded = json.loads(html[start:end])
        assert embedded["project_slug"] == "regression-test"
        assert embedded["phase"] == "coding"
