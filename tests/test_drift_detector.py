"""Tests for drift detection engine."""

import json

import pytest

from claude_cli.drift.detector import (
    create_rules_template,
    detect_drift,
    load_drift_rules,
    run_check,
)


@pytest.fixture
def drift_project(tmp_path):
    """Create a project with drift rules and matching code."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    (claude_dir / "manifest.yaml").write_text("phase: coding\n")

    # Source code structure
    core_dir = tmp_path / "src" / "core"
    core_dir.mkdir(parents=True)
    (core_dir / "ports.py").write_text("class UserPort:\n    pass\n")

    adapters_dir = tmp_path / "src" / "adapters"
    adapters_dir.mkdir(parents=True)
    (adapters_dir / "http.py").write_text("import requests\n")

    # Drift rules
    rules_path = claude_dir / "drift_rules.yaml"
    rules_path.write_text("""\
schema_version: "1.0"
rules:
  - decision_id: "ADR-001"
    title: "Hexagonal Architecture"
    assertions:
      - type: "grep_exists"
        pattern: "class.*Port"
        path: "src/core/"
        description: "Core domain defines Port interfaces"
      - type: "file_exists"
        path: "src/adapters/"
        description: "Adapters directory exists"
      - type: "grep_absent"
        pattern: "import requests"
        path: "src/core/"
        description: "Core domain has no direct HTTP calls"

  - decision_id: "ADR-002"
    title: "Config-Driven Scoring"
    assertions:
      - type: "file_exists"
        path: "config/scoring/"
        description: "Scoring config directory exists"
""")

    return tmp_path


class TestLoadDriftRules:
    def test_loads_valid_rules(self, drift_project):
        rules = load_drift_rules(drift_project / ".claude" / "drift_rules.yaml")
        assert len(rules) == 2
        assert rules[0]["decision_id"] == "ADR-001"

    def test_returns_empty_for_missing_file(self, tmp_path):
        rules = load_drift_rules(tmp_path / "nonexistent.yaml")
        assert rules == []

    def test_returns_empty_for_empty_file(self, tmp_path):
        empty = tmp_path / "empty.yaml"
        empty.write_text("")
        rules = load_drift_rules(empty)
        assert rules == []

    def test_returns_empty_for_malformed_yaml(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("rules: not_a_list")
        rules = load_drift_rules(bad)
        assert rules == []


class TestRunCheck:
    def test_grep_exists_pass(self, drift_project):
        rule = {
            "decision_id": "ADR-001",
            "title": "Test",
            "assertions": [
                {
                    "type": "grep_exists",
                    "pattern": "class.*Port",
                    "path": "src/core/",
                    "description": "Port interfaces exist",
                }
            ],
        }
        checks = run_check(rule, drift_project)
        assert len(checks) == 1
        assert checks[0].passed is True
        assert checks[0].assertion_type == "grep_exists"

    def test_grep_exists_fail(self, drift_project):
        rule = {
            "decision_id": "ADR-001",
            "title": "Test",
            "assertions": [
                {
                    "type": "grep_exists",
                    "pattern": "class.*NonExistent",
                    "path": "src/core/",
                    "description": "Should not match",
                }
            ],
        }
        checks = run_check(rule, drift_project)
        assert len(checks) == 1
        assert checks[0].passed is False

    def test_grep_absent_pass(self, drift_project):
        rule = {
            "decision_id": "ADR-001",
            "title": "Test",
            "assertions": [
                {
                    "type": "grep_absent",
                    "pattern": "import requests",
                    "path": "src/core/",
                    "description": "No HTTP in core",
                }
            ],
        }
        checks = run_check(rule, drift_project)
        assert len(checks) == 1
        assert checks[0].passed is True

    def test_grep_absent_fail(self, drift_project):
        rule = {
            "decision_id": "ADR-001",
            "title": "Test",
            "assertions": [
                {
                    "type": "grep_absent",
                    "pattern": "import requests",
                    "path": "src/adapters/",
                    "description": "Should fail - requests present",
                }
            ],
        }
        checks = run_check(rule, drift_project)
        assert len(checks) == 1
        assert checks[0].passed is False

    def test_file_exists_pass(self, drift_project):
        rule = {
            "decision_id": "ADR-001",
            "title": "Test",
            "assertions": [
                {
                    "type": "file_exists",
                    "path": "src/adapters/",
                    "description": "Adapters dir exists",
                }
            ],
        }
        checks = run_check(rule, drift_project)
        assert len(checks) == 1
        assert checks[0].passed is True

    def test_file_exists_fail(self, drift_project):
        rule = {
            "decision_id": "ADR-001",
            "title": "Test",
            "assertions": [
                {
                    "type": "file_exists",
                    "path": "src/nonexistent/",
                    "description": "Should fail",
                }
            ],
        }
        checks = run_check(rule, drift_project)
        assert len(checks) == 1
        assert checks[0].passed is False

    def test_file_absent_pass(self, drift_project):
        rule = {
            "decision_id": "ADR-001",
            "title": "Test",
            "assertions": [
                {
                    "type": "file_absent",
                    "path": "src/legacy/",
                    "description": "Legacy dir removed",
                }
            ],
        }
        checks = run_check(rule, drift_project)
        assert len(checks) == 1
        assert checks[0].passed is True

    def test_file_absent_fail(self, drift_project):
        rule = {
            "decision_id": "ADR-001",
            "title": "Test",
            "assertions": [
                {
                    "type": "file_absent",
                    "path": "src/adapters/",
                    "description": "Should fail - exists",
                }
            ],
        }
        checks = run_check(rule, drift_project)
        assert len(checks) == 1
        assert checks[0].passed is False

    def test_unknown_assertion_type(self, drift_project):
        rule = {
            "decision_id": "ADR-001",
            "title": "Test",
            "assertions": [{"type": "magic_check", "description": "Unknown"}],
        }
        checks = run_check(rule, drift_project)
        assert len(checks) == 1
        assert checks[0].passed is False
        assert "Unknown assertion type" in checks[0].evidence

    def test_grep_on_missing_path(self, drift_project):
        rule = {
            "decision_id": "ADR-001",
            "title": "Test",
            "assertions": [
                {
                    "type": "grep_exists",
                    "pattern": "anything",
                    "path": "nonexistent/",
                    "description": "Missing path",
                }
            ],
        }
        checks = run_check(rule, drift_project)
        assert checks[0].passed is False


class TestDetectDrift:
    def test_end_to_end(self, drift_project):
        report = detect_drift(drift_project)
        assert report.project_slug == drift_project.name
        assert report.total == 4
        # ADR-001: grep_exists pass, file_exists pass, grep_absent pass
        # ADR-002: file_exists fail (config/scoring/ missing)
        assert report.passed == 3
        assert report.failed == 1
        assert report.has_drift is True

    def test_no_rules_file(self, tmp_path):
        (tmp_path / ".claude").mkdir()
        report = detect_drift(tmp_path)
        assert report.total == 0
        assert report.passed == 0
        assert report.failed == 0
        assert report.has_drift is False

    def test_empty_rules(self, tmp_path):
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "drift_rules.yaml").write_text("schema_version: '1.0'\nrules: []\n")
        report = detect_drift(tmp_path)
        assert report.total == 0
        assert report.has_drift is False


class TestDriftReportSerialization:
    def test_to_json(self, drift_project):
        report = detect_drift(drift_project)
        data = json.loads(report.to_json())
        assert data["project_slug"] == drift_project.name
        assert data["total"] == 4
        assert data["has_drift"] is True
        assert len(data["checks"]) == 4

    def test_to_markdown(self, drift_project):
        report = detect_drift(drift_project)
        md = report.to_markdown()
        assert "# Drift Report:" in md
        assert "ADR-001" in md
        assert "ADR-002" in md
        assert "[PASS]" in md
        assert "[FAIL]" in md

    def test_empty_report_markdown(self, tmp_path):
        (tmp_path / ".claude").mkdir()
        report = detect_drift(tmp_path)
        md = report.to_markdown()
        assert "No drift rules configured" in md


class TestCreateRulesTemplate:
    def test_creates_template_file(self, tmp_path):
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        path = create_rules_template(tmp_path)
        assert path.exists()
        assert path.name == "drift_rules.yaml"
        content = path.read_text()
        assert "schema_version" in content
        assert "ADR-001" in content

    def test_creates_claude_dir_if_missing(self, tmp_path):
        path = create_rules_template(tmp_path)
        assert path.exists()
        assert (tmp_path / ".claude").is_dir()
