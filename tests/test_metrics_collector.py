"""Tests for agent metrics collection and aggregation."""

import json

import pytest

from claude_cli.metrics.collector import (
    AgentRun,
    AgentStats,
    MetricsReport,
    aggregate_metrics,
    collect_from_batch_ledgers,
    collect_from_evidence,
    load_metrics_history,
    store_metrics,
)


@pytest.fixture
def sample_runs():
    """Create sample agent runs for testing."""
    return [
        AgentRun(
            agent_type="back",
            project_slug="project-a",
            started_at="2026-01-01T00:00:00",
            duration_ms=5000,
            total_tokens=1000,
            tool_uses=10,
            status="completed",
            task_ids=["T-001"],
        ),
        AgentRun(
            agent_type="back",
            project_slug="project-a",
            started_at="2026-01-02T00:00:00",
            duration_ms=3000,
            total_tokens=800,
            tool_uses=8,
            status="completed",
            task_ids=["T-002"],
        ),
        AgentRun(
            agent_type="front",
            project_slug="project-b",
            started_at="2026-01-01T00:00:00",
            duration_ms=4000,
            total_tokens=1200,
            tool_uses=15,
            status="failed",
            task_ids=["T-003"],
        ),
        AgentRun(
            agent_type="qa",
            project_slug="project-a",
            started_at="2026-01-03T00:00:00",
            duration_ms=2000,
            total_tokens=500,
            tool_uses=5,
            status="completed",
            task_ids=[],
        ),
    ]


@pytest.fixture
def batch_project(tmp_path):
    """Create a project with batch ledger files."""
    project = tmp_path / "test-project"
    claude_dir = project / ".claude"
    (claude_dir / "batch" / "batch-001").mkdir(parents=True)
    (claude_dir / "manifest.yaml").write_text("phase: coding\n")

    ledger_content = """\
schema_version: "1.0"
agent_type: back
created_at: "2026-01-01T00:00:00"
items:
  - name: "task-1"
    status: done
    agent_type: back
    started_at: "2026-01-01T00:00:00"
    duration_ms: 5000
    total_tokens: 1000
    tool_uses: 10
    task_ids:
      - T-001
  - name: "task-2"
    status: failed
    agent_type: back
    started_at: "2026-01-01T01:00:00"
    duration_ms: 3000
    total_tokens: 800
    tool_uses: 8
  - name: "task-3"
    status: active
    agent_type: back
"""
    (claude_dir / "batch" / "batch-001" / "ledger.yaml").write_text(ledger_content)
    return tmp_path


@pytest.fixture
def evidence_project(tmp_path):
    """Create a project with evidence agent_runs.json."""
    claude_dir = tmp_path / ".claude" / "evidence"
    claude_dir.mkdir(parents=True)
    runs = [
        {
            "agent_type": "qa",
            "project_slug": "test-project",
            "started_at": "2026-01-05T00:00:00",
            "duration_ms": 2000,
            "total_tokens": 500,
            "tool_uses": 5,
            "status": "completed",
            "task_ids": ["T-010"],
        }
    ]
    (claude_dir / "agent_runs.json").write_text(json.dumps(runs))
    return tmp_path


class TestCollectFromBatchLedgers:
    def test_collects_completed_and_failed(self, batch_project):
        runs = collect_from_batch_ledgers(batch_project)
        assert len(runs) == 2
        statuses = {r.status for r in runs}
        assert statuses == {"completed", "failed"}

    def test_skips_active_items(self, batch_project):
        runs = collect_from_batch_ledgers(batch_project)
        assert all(r.status != "active" for r in runs)

    def test_extracts_fields(self, batch_project):
        runs = collect_from_batch_ledgers(batch_project)
        completed = [r for r in runs if r.status == "completed"][0]
        assert completed.agent_type == "back"
        assert completed.duration_ms == 5000
        assert completed.total_tokens == 1000
        assert completed.tool_uses == 10
        assert completed.task_ids == ["T-001"]

    def test_empty_directory(self, tmp_path):
        runs = collect_from_batch_ledgers(tmp_path)
        assert runs == []

    def test_missing_ledger(self, tmp_path):
        project = tmp_path / "project"
        claude_dir = project / ".claude"
        claude_dir.mkdir(parents=True)
        (claude_dir / "manifest.yaml").write_text("phase: coding\n")
        runs = collect_from_batch_ledgers(tmp_path)
        assert runs == []


class TestCollectFromEvidence:
    def test_collects_runs(self, evidence_project):
        runs = collect_from_evidence(evidence_project)
        assert len(runs) == 1
        assert runs[0].agent_type == "qa"
        assert runs[0].status == "completed"
        assert runs[0].task_ids == ["T-010"]

    def test_missing_evidence(self, tmp_path):
        runs = collect_from_evidence(tmp_path)
        assert runs == []

    def test_invalid_json(self, tmp_path):
        evidence_dir = tmp_path / ".claude" / "evidence"
        evidence_dir.mkdir(parents=True)
        (evidence_dir / "agent_runs.json").write_text("not json")
        runs = collect_from_evidence(tmp_path)
        assert runs == []


class TestAggregateMetrics:
    def test_aggregates_by_agent(self, sample_runs):
        report = aggregate_metrics(sample_runs)
        assert report.total_runs == 4
        assert "back" in report.by_agent
        assert "front" in report.by_agent
        assert "qa" in report.by_agent

    def test_back_stats(self, sample_runs):
        report = aggregate_metrics(sample_runs)
        back = report.by_agent["back"]
        assert back.runs == 2
        assert back.avg_duration_ms == 4000.0
        assert back.avg_tokens == 900.0
        assert back.avg_tool_uses == 9.0
        assert back.success_rate == 1.0

    def test_front_stats(self, sample_runs):
        report = aggregate_metrics(sample_runs)
        front = report.by_agent["front"]
        assert front.runs == 1
        assert front.success_rate == 0.0

    def test_by_project(self, sample_runs):
        report = aggregate_metrics(sample_runs)
        assert report.by_project["project-a"] == 3
        assert report.by_project["project-b"] == 1

    def test_empty_runs(self):
        report = aggregate_metrics([])
        assert report.total_runs == 0
        assert report.by_agent == {}
        assert report.by_project == {}


class TestMetricsReportSerialization:
    def test_to_json(self, sample_runs):
        report = aggregate_metrics(sample_runs)
        data = json.loads(report.to_json())
        assert data["total_runs"] == 4
        assert "back" in data["by_agent"]
        assert data["by_agent"]["back"]["runs"] == 2

    def test_to_markdown(self, sample_runs):
        report = aggregate_metrics(sample_runs)
        md = report.to_markdown()
        assert "# Agent Metrics Report" in md
        assert "back" in md
        assert "front" in md

    def test_empty_report_markdown(self):
        report = aggregate_metrics([])
        md = report.to_markdown()
        assert "No agent runs recorded" in md


class TestDuckDBRoundTrip:
    def test_store_and_load(self, tmp_path, sample_runs):
        db_path = tmp_path / "test_metrics.duckdb"
        report = aggregate_metrics(sample_runs)
        store_metrics(report, db_path)

        history = load_metrics_history(db_path, days=30)
        assert len(history) == 1
        loaded = history[0]
        assert loaded.total_runs == report.total_runs
        assert set(loaded.by_agent.keys()) == set(report.by_agent.keys())

    def test_load_from_nonexistent_db(self, tmp_path):
        db_path = tmp_path / "nonexistent.duckdb"
        history = load_metrics_history(db_path)
        assert history == []

    def test_multiple_reports(self, tmp_path, sample_runs):
        db_path = tmp_path / "test_metrics.duckdb"
        report1 = aggregate_metrics(sample_runs)
        store_metrics(report1, db_path)
        report2 = aggregate_metrics(sample_runs[:2])
        store_metrics(report2, db_path)

        history = load_metrics_history(db_path, days=30)
        assert len(history) == 2
