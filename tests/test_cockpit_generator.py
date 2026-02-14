"""Tests for the cockpit dashboard generator."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from claude_cli.cockpit.generator import collect_data, find_project_root, render_html


@pytest.fixture
def project_dir(tmp_path):
    """Create a minimal governed project structure."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()

    # Manifest
    manifest = claude_dir / "manifest.yaml"
    manifest.write_text(
        """\
schema_version: "1.4"
project_slug: "test-project"
project_name: "Test Project"
created: "2026-02-14T00:00:00Z"
last_updated: "2026-02-14T12:00:00Z"
phase: "coding"
phase_started: "2026-02-14T10:00:00Z"

artifact_versions:
  spec:
    version: 2
    file: ".claude/artifacts/002_spec_v2.md"
  tasklist:
    version: 1
    file: ".claude/artifacts/003_tasklist_v1.md"

outstanding:
  tasks:
    - id: "T001"
      title: "Create user model"
      status: "completed"
    - id: "T002"
      title: "Create auth service"
      status: "in_progress"
    - id: "T003"
      title: "Create API routes"
      status: "pending"
    - id: "T004"
      title: "Integration tests"
      status: "pending"
      blocked_by: ["T002"]
  remediation:
    - id: "BUG-001"
      priority: "high"
      status: "pending"
    - id: "BUG-002"
      priority: "critical"
      status: "pending"
    - id: "IMPROVE-001"
      priority: "medium"
      status: "pending"
"""
    )

    # Evidence
    evidence_dir = claude_dir / "evidence"
    evidence_dir.mkdir()
    gates = evidence_dir / "quality_gates_run.json"
    gates.write_text(
        json.dumps(
            {
                "result": "pass",
                "timestamp": "2026-02-14T11:30:00Z",
                "gates": [
                    {"name": "lint", "result": "pass"},
                    {"name": "type_check", "result": "pass"},
                    {"name": "tests", "result": "pass"},
                ],
            }
        )
    )

    # Remediation inbox
    inbox_dir = claude_dir / "remediation" / "inbox"
    inbox_dir.mkdir(parents=True)
    (inbox_dir / "BUG-001_qa_2026-02-14.md").write_text("---\nid: BUG-001\n---\n")

    # Outbox
    for status in ("pending", "active", "completed", "rejected"):
        d = claude_dir / "outbox" / status
        d.mkdir(parents=True)
    (claude_dir / "outbox" / "pending" / "OBX-001.md").write_text("task")
    (claude_dir / "outbox" / "completed" / "OBX-002.md").write_text("done")

    # Artifacts dir
    (claude_dir / "artifacts").mkdir()

    return tmp_path


class TestFindProjectRoot:
    def test_finds_root_with_manifest(self, project_dir):
        # Start from a subdirectory
        sub = project_dir / "src" / "components"
        sub.mkdir(parents=True)
        result = find_project_root(sub)
        assert result == project_dir

    def test_returns_none_without_manifest(self, tmp_path):
        result = find_project_root(tmp_path)
        assert result is None


class TestCollectData:
    def test_collects_project_metadata(self, project_dir):
        data = collect_data(project_dir)
        assert data["project_slug"] == "test-project"
        assert data["project_name"] == "Test Project"
        assert data["phase"] == "coding"

    def test_counts_tasks_by_status(self, project_dir):
        data = collect_data(project_dir)
        assert data["tasks"]["completed"] == 1
        assert data["tasks"]["in_progress"] == 1
        assert data["tasks"]["pending"] == 1
        assert data["tasks"]["blocked"] == 1

    def test_reads_quality_gates(self, project_dir):
        data = collect_data(project_dir)
        assert data["quality_gates"] is not None
        assert data["quality_gates"]["result"] == "pass"

    def test_counts_remediation(self, project_dir):
        data = collect_data(project_dir)
        assert data["remediation"]["total"] >= 3
        assert data["remediation"]["critical"] == 1
        assert data["remediation"]["high"] == 1

    def test_counts_outbox(self, project_dir):
        data = collect_data(project_dir)
        assert data["outbox"]["pending"] == 1
        assert data["outbox"]["completed"] == 1
        assert data["outbox"]["active"] == 0
        assert data["outbox"]["rejected"] == 0

    def test_reads_artifact_versions(self, project_dir):
        data = collect_data(project_dir)
        assert "spec" in data["artifacts"]
        assert data["artifacts"]["spec"]["version"] == 2

    def test_handles_missing_evidence(self, project_dir):
        (project_dir / ".claude" / "evidence" / "quality_gates_run.json").unlink()
        data = collect_data(project_dir)
        assert data["quality_gates"] is None

    def test_handles_missing_outbox(self, tmp_path):
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "manifest.yaml").write_text("phase: coding\n")
        data = collect_data(tmp_path)
        assert data["outbox"]["pending"] == 0

    @patch("claude_cli.cockpit.generator.subprocess.run")
    def test_collects_git_commits(self, mock_run, project_dir):
        mock_run.return_value = type(
            "Result", (), {"returncode": 0, "stdout": "abc123|feat: add auth|2026-02-14 10:00:00 +0000\ndef456|fix: typo|2026-02-13 09:00:00 +0000\n"}
        )()
        data = collect_data(project_dir)
        assert len(data["commits"]) == 2
        assert data["commits"][0]["hash"] == "abc123"

    @patch("claude_cli.cockpit.generator.subprocess.run")
    def test_handles_git_failure(self, mock_run, project_dir):
        mock_run.return_value = type("Result", (), {"returncode": 1, "stdout": ""})()
        data = collect_data(project_dir)
        assert data["commits"] == []


class TestRenderHtml:
    def test_produces_valid_html(self, project_dir):
        data = collect_data(project_dir)
        html = render_html(data)
        assert "<!DOCTYPE html>" in html
        assert "COCKPIT_DATA" in html
        assert data["project_name"] in html

    def test_embeds_data_as_json(self, project_dir):
        data = collect_data(project_dir)
        html = render_html(data)
        # Extract the JSON from the script tag
        start = html.index("COCKPIT_DATA = ") + len("COCKPIT_DATA = ")
        end = html.index(";\n", start)
        embedded = json.loads(html[start:end])
        assert embedded["project_slug"] == "test-project"
        assert embedded["phase"] == "coding"

    def test_contains_all_sections(self, project_dir):
        data = collect_data(project_dir)
        html = render_html(data)
        assert "Task Progress" in html
        assert "Quality Gates" in html
        assert "Remediation" in html
        assert "Agent Activity" in html
        assert "Recent Commits" in html
        assert "Artifact Versions" in html

    def test_uses_dark_theme(self, project_dir):
        data = collect_data(project_dir)
        html = render_html(data)
        assert "#0f172a" in html  # background
        assert "#1e293b" in html  # card background


class TestGenerateCockpit:
    def test_writes_html_file(self, project_dir):
        from claude_cli.cockpit.generator import generate_cockpit

        output = generate_cockpit(project_dir)
        assert output.exists()
        assert output.name == "cockpit.html"
        assert output.parent.name == ".claude"
        content = output.read_text()
        assert "<!DOCTYPE html>" in content

    def test_custom_output_path(self, project_dir, tmp_path):
        from claude_cli.cockpit.generator import generate_cockpit

        custom = tmp_path / "dashboard.html"
        output = generate_cockpit(project_dir, output=custom)
        assert output == custom
        assert custom.exists()

    def test_raises_without_manifest(self, tmp_path):
        from claude_cli.cockpit.generator import generate_cockpit

        # Pass a project_root that has no manifest
        bare_dir = tmp_path / "no-project"
        bare_dir.mkdir()
        # generate_cockpit with explicit project_root won't search parents,
        # but collect_data will still work (just return defaults).
        # Test find_project_root instead for the "not found" case.
        result = find_project_root(bare_dir)
        # tmp_path is under /tmp which has no manifest, should return None
        # (unless the test runner's cwd has one)
        # This is environment-dependent, so test the generator's explicit error
        # by monkeypatching
        with patch("claude_cli.cockpit.generator.find_project_root", return_value=None):
            with pytest.raises(FileNotFoundError):
                generate_cockpit()
