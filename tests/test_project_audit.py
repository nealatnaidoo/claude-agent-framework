"""Tests for project audit engine."""

import json

import pytest

from claude_cli.audit.auditor import (
    AuditFinding,
    AuditReport,
    SectionResult,
    audit_artifacts,
    audit_architecture,
    audit_governance,
    audit_manifest,
    audit_project,
    calculate_score,
)


@pytest.fixture
def compliant_project(tmp_path):
    """Create a fully compliant project structure."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()

    # Manifest
    (claude_dir / "manifest.yaml").write_text("""\
schema_version: "1.0"
project_slug: test-project
project_name: Test Project
phase: coding
last_updated: "2026-02-14T00:00:00+00:00"
outstanding:
  tasks:
    - id: T-001
      status: completed
    - id: T-002
      status: pending
artifact_versions:
  spec:
    version: 1
    file: .claude/artifacts/002_spec_v1.md
""")

    # Artifacts
    artifacts_dir = claude_dir / "artifacts"
    artifacts_dir.mkdir()
    (artifacts_dir / "002_spec_v1.md").write_text("# Spec\n")
    (artifacts_dir / "003_tasklist_v1.md").write_text("# Tasklist\n")

    # Evolution
    evo_dir = claude_dir / "evolution"
    evo_dir.mkdir()
    (evo_dir / "evolution.md").write_text("# Evolution\n")
    (evo_dir / "decisions.md").write_text("# Decisions\n")

    # Evidence
    evidence_dir = claude_dir / "evidence"
    evidence_dir.mkdir()
    (evidence_dir / "quality_gates_run.json").write_text("{}")

    # Remediation (empty inbox)
    (claude_dir / "remediation" / "inbox").mkdir(parents=True)

    # Clean core
    core_dir = tmp_path / "src" / "core"
    core_dir.mkdir(parents=True)
    (core_dir / "service.py").write_text("class UserService:\n    pass\n")

    # Tests
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_service.py").write_text("def test_user(): pass\n")

    return tmp_path


@pytest.fixture
def minimal_project(tmp_path):
    """Create a bare minimum project (just manifest)."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    (claude_dir / "manifest.yaml").write_text("phase: init\n")
    return tmp_path


class TestAuditManifest:
    def test_valid_manifest(self, compliant_project):
        findings = audit_manifest(compliant_project)
        # Should have no critical/high findings
        critical_high = [f for f in findings if f.severity in ("critical", "high")]
        assert len(critical_high) == 0

    def test_missing_manifest(self, tmp_path):
        (tmp_path / ".claude").mkdir()
        findings = audit_manifest(tmp_path)
        assert len(findings) == 1
        assert findings[0].rule_id == "PA-001"
        assert findings[0].severity == "critical"

    def test_missing_schema_version(self, tmp_path):
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "manifest.yaml").write_text("phase: coding\n")
        findings = audit_manifest(tmp_path)
        pa002 = [f for f in findings if f.rule_id == "PA-002"]
        assert len(pa002) == 1

    def test_invalid_phase(self, tmp_path):
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "manifest.yaml").write_text("schema_version: '1.0'\nphase: nonexistent\n")
        findings = audit_manifest(tmp_path)
        pa003 = [f for f in findings if f.rule_id == "PA-003"]
        assert len(pa003) == 1

    def test_missing_artifact_file(self, tmp_path):
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "manifest.yaml").write_text("""\
schema_version: "1.0"
phase: coding
artifact_versions:
  spec:
    version: 1
    file: .claude/artifacts/missing.md
""")
        findings = audit_manifest(tmp_path)
        pa004 = [f for f in findings if f.rule_id == "PA-004"]
        assert len(pa004) == 1

    def test_invalid_task_status(self, tmp_path):
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "manifest.yaml").write_text("""\
schema_version: "1.0"
phase: coding
outstanding:
  tasks:
    - id: T-001
      status: bogus
""")
        findings = audit_manifest(tmp_path)
        pa005 = [f for f in findings if f.rule_id == "PA-005"]
        assert len(pa005) == 1


class TestAuditArtifacts:
    def test_compliant_artifacts(self, compliant_project):
        findings = audit_artifacts(compliant_project)
        # Evolution and decisions exist, naming is correct
        pa012 = [f for f in findings if f.rule_id == "PA-012"]
        pa013 = [f for f in findings if f.rule_id == "PA-013"]
        assert len(pa012) == 0
        assert len(pa013) == 0

    def test_missing_evolution(self, minimal_project):
        findings = audit_artifacts(minimal_project)
        pa012 = [f for f in findings if f.rule_id == "PA-012"]
        assert len(pa012) == 1

    def test_missing_decisions(self, minimal_project):
        findings = audit_artifacts(minimal_project)
        pa013 = [f for f in findings if f.rule_id == "PA-013"]
        assert len(pa013) == 1

    def test_bad_artifact_naming(self, tmp_path):
        claude_dir = tmp_path / ".claude"
        artifacts_dir = claude_dir / "artifacts"
        artifacts_dir.mkdir(parents=True)
        (claude_dir / "manifest.yaml").write_text("phase: init\n")
        (artifacts_dir / "bad_name.md").write_text("content")

        findings = audit_artifacts(tmp_path)
        pa011 = [f for f in findings if f.rule_id == "PA-011"]
        assert len(pa011) == 1

    def test_missing_required_artifacts_for_phase(self, tmp_path):
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "manifest.yaml").write_text("phase: coding\n")
        # No artifacts directory at all
        findings = audit_artifacts(tmp_path)
        pa010 = [f for f in findings if f.rule_id == "PA-010"]
        assert len(pa010) == 1


class TestAuditArchitecture:
    def test_clean_core(self, compliant_project):
        findings = audit_architecture(compliant_project)
        assert len(findings) == 0

    def test_adapter_import_in_core(self, tmp_path):
        core_dir = tmp_path / "src" / "core"
        core_dir.mkdir(parents=True)
        (core_dir / "bad.py").write_text("import requests\n")
        findings = audit_architecture(tmp_path)
        pa020 = [f for f in findings if f.rule_id == "PA-020"]
        assert len(pa020) == 1

    def test_datetime_now_in_core(self, tmp_path):
        core_dir = tmp_path / "src" / "core"
        core_dir.mkdir(parents=True)
        (core_dir / "svc.py").write_text("from datetime import datetime\nnow = datetime.now()\n")
        findings = audit_architecture(tmp_path)
        pa021 = [f for f in findings if f.rule_id == "PA-021"]
        assert len(pa021) == 1

    def test_hardcoded_secret(self, tmp_path):
        core_dir = tmp_path / "src" / "core"
        core_dir.mkdir(parents=True)
        (core_dir / "config.py").write_text('api_key = "sk-12345678abcdefgh"\n')
        findings = audit_architecture(tmp_path)
        pa022 = [f for f in findings if f.rule_id == "PA-022"]
        assert len(pa022) == 1

    def test_no_core_directory(self, tmp_path):
        findings = audit_architecture(tmp_path)
        assert len(findings) == 0


class TestAuditGovernance:
    def test_clean_governance(self, compliant_project):
        findings = audit_governance(compliant_project)
        assert len(findings) == 0

    def test_stale_remediation_inbox(self, tmp_path):
        inbox_dir = tmp_path / ".claude" / "remediation" / "inbox"
        inbox_dir.mkdir(parents=True)
        for i in range(6):
            (inbox_dir / f"BUG-{i:03d}.md").write_text("bug")
        findings = audit_governance(tmp_path)
        pa030 = [f for f in findings if f.rule_id == "PA-030"]
        assert len(pa030) == 1

    def test_missing_quality_gate_evidence(self, tmp_path):
        (tmp_path / ".claude").mkdir()
        findings = audit_governance(tmp_path)
        pa031 = [f for f in findings if f.rule_id == "PA-031"]
        assert len(pa031) == 1

    def test_outbox_backlog(self, tmp_path):
        pending_dir = tmp_path / ".claude" / "outbox" / "pending"
        pending_dir.mkdir(parents=True)
        for i in range(4):
            (pending_dir / f"OBX-{i:03d}.md").write_text("task")
        findings = audit_governance(tmp_path)
        pa032 = [f for f in findings if f.rule_id == "PA-032"]
        assert len(pa032) == 1


class TestCalculateScore:
    def test_perfect_score(self):
        score, grade = calculate_score([])
        assert score == 100
        assert grade == "A"

    def test_critical_deduction(self):
        findings = [
            AuditFinding("test", "PA-001", "critical", "t", "d"),
        ]
        score, grade = calculate_score(findings)
        assert score == 75
        assert grade == "B"

    def test_high_deduction(self):
        findings = [
            AuditFinding("test", "PA-001", "high", "t", "d"),
        ]
        score, grade = calculate_score(findings)
        assert score == 90
        assert grade == "A"

    def test_medium_deduction(self):
        findings = [
            AuditFinding("test", "PA-001", "medium", "t", "d"),
        ]
        score, grade = calculate_score(findings)
        assert score == 97

    def test_floor_at_zero(self):
        findings = [
            AuditFinding("test", f"PA-{i:03d}", "critical", "t", "d")
            for i in range(10)
        ]
        score, grade = calculate_score(findings)
        assert score == 0
        assert grade == "F"

    def test_grade_boundaries(self):
        # D grade: 40-59
        findings = [
            AuditFinding("test", "PA-001", "critical", "t", "d"),
            AuditFinding("test", "PA-002", "high", "t", "d"),
            AuditFinding("test", "PA-003", "high", "t", "d"),
        ]
        score, grade = calculate_score(findings)
        assert score == 55
        assert grade == "D"


class TestAuditProject:
    def test_compliant_project(self, compliant_project):
        report = audit_project(compliant_project)
        assert report.project_slug == compliant_project.name
        assert report.score > 0
        assert report.grade in ("A", "B", "C", "D", "F")
        assert "manifest" in report.sections
        assert "artifacts" in report.sections
        assert "architecture" in report.sections
        assert "governance" in report.sections

    def test_report_serialization_json(self, compliant_project):
        report = audit_project(compliant_project)
        data = json.loads(report.to_json())
        assert "score" in data
        assert "grade" in data
        assert "findings" in data
        assert "sections" in data

    def test_report_serialization_markdown(self, compliant_project):
        report = audit_project(compliant_project)
        md = report.to_markdown()
        assert "# Audit Report:" in md
        assert "Score" in md
        assert "Grade" in md

    def test_minimal_project(self, minimal_project):
        report = audit_project(minimal_project)
        assert report.total_findings > 0
        assert report.score < 100

    def test_portfolio_audit(self, tmp_path):
        """Test auditing multiple projects."""
        for name in ["proj-a", "proj-b"]:
            proj = tmp_path / name
            claude_dir = proj / ".claude"
            claude_dir.mkdir(parents=True)
            (claude_dir / "manifest.yaml").write_text(f"phase: init\nproject_slug: {name}\n")

        reports = []
        for proj in sorted(tmp_path.iterdir()):
            if (proj / ".claude" / "manifest.yaml").exists():
                reports.append(audit_project(proj))

        assert len(reports) == 2
        assert reports[0].project_slug == "proj-a"
        assert reports[1].project_slug == "proj-b"
