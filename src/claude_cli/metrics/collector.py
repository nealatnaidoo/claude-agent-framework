"""Agent performance metrics collection and aggregation.

Collects agent run data from batch ledgers and evidence files,
aggregates into reports, and stores in DuckDB for trending.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from claude_cli.cockpit.generator import read_yaml_simple


@dataclass
class AgentRun:
    """A single agent execution record."""

    agent_type: str
    project_slug: str
    started_at: str
    duration_ms: int
    total_tokens: int
    tool_uses: int
    status: str  # "completed", "failed", "timeout"
    task_ids: list[str] = field(default_factory=list)


@dataclass
class AgentStats:
    """Aggregated statistics for an agent type."""

    runs: int
    avg_duration_ms: float
    avg_tokens: float
    avg_tool_uses: float
    success_rate: float


@dataclass
class MetricsReport:
    """Aggregated metrics report across agents and projects."""

    generated_at: str
    total_runs: int
    by_agent: dict[str, AgentStats] = field(default_factory=dict)
    by_project: dict[str, int] = field(default_factory=dict)

    def to_json(self) -> str:
        """Serialize report to JSON."""
        return json.dumps(
            {
                "generated_at": self.generated_at,
                "total_runs": self.total_runs,
                "by_agent": {
                    name: {
                        "runs": stats.runs,
                        "avg_duration_ms": stats.avg_duration_ms,
                        "avg_tokens": stats.avg_tokens,
                        "avg_tool_uses": stats.avg_tool_uses,
                        "success_rate": stats.success_rate,
                    }
                    for name, stats in self.by_agent.items()
                },
                "by_project": self.by_project,
            },
            indent=2,
        )

    def to_markdown(self) -> str:
        """Serialize report to markdown."""
        lines = [
            "# Agent Metrics Report",
            "",
            f"**Generated**: {self.generated_at}  ",
            f"**Total Runs**: {self.total_runs}",
            "",
        ]

        if not self.by_agent:
            lines.append("No agent runs recorded.")
            return "\n".join(lines)

        lines.append("## By Agent")
        lines.append("")
        lines.append("| Agent | Runs | Avg Duration | Avg Tokens | Avg Tools | Success Rate |")
        lines.append("|-------|------|-------------|------------|-----------|-------------|")
        for name, stats in sorted(self.by_agent.items()):
            lines.append(
                f"| {name} | {stats.runs} | {stats.avg_duration_ms:.0f}ms "
                f"| {stats.avg_tokens:.0f} | {stats.avg_tool_uses:.1f} "
                f"| {stats.success_rate:.1%} |"
            )
        lines.append("")

        if self.by_project:
            lines.append("## By Project")
            lines.append("")
            for proj, count in sorted(self.by_project.items()):
                lines.append(f"- **{proj}**: {count} runs")
            lines.append("")

        return "\n".join(lines)


def collect_from_batch_ledgers(base_dir: Path) -> list[AgentRun]:
    """Scan projects for batch ledger files and extract agent runs.

    Looks for: {project}/.claude/batch/*/ledger.yaml
    """
    runs: list[AgentRun] = []

    for manifest in sorted(base_dir.glob("*/.claude/manifest.yaml")):
        project_root = manifest.parent.parent
        batch_dir = project_root / ".claude" / "batch"
        if not batch_dir.exists():
            continue

        for ledger_path in sorted(batch_dir.glob("*/ledger.yaml")):
            ledger = read_yaml_simple(ledger_path)
            if not ledger:
                continue

            items = ledger.get("items", [])
            if not isinstance(items, list):
                continue

            for item in items:
                if not isinstance(item, dict):
                    continue

                status = item.get("status", "unknown")
                if status not in ("done", "failed"):
                    continue

                agent_type = item.get("agent_type", ledger.get("agent_type", "unknown"))
                started = item.get("started_at", ledger.get("created_at", ""))
                duration = item.get("duration_ms", 0)
                tokens = item.get("total_tokens", 0)
                tools = item.get("tool_uses", 0)
                task_ids = item.get("task_ids", [])
                if not isinstance(task_ids, list):
                    task_ids = [str(task_ids)] if task_ids else []

                mapped_status = "completed" if status == "done" else "failed"
                runs.append(
                    AgentRun(
                        agent_type=str(agent_type),
                        project_slug=project_root.name,
                        started_at=str(started),
                        duration_ms=int(duration) if duration else 0,
                        total_tokens=int(tokens) if tokens else 0,
                        tool_uses=int(tools) if tools else 0,
                        status=mapped_status,
                        task_ids=[str(t) for t in task_ids],
                    )
                )

    return runs


def collect_from_evidence(project_root: Path) -> list[AgentRun]:
    """Collect agent run data from evidence files.

    Looks for: {project}/.claude/evidence/agent_runs.json
    """
    runs: list[AgentRun] = []
    evidence_file = project_root / ".claude" / "evidence" / "agent_runs.json"

    if not evidence_file.exists():
        return runs

    try:
        data = json.loads(evidence_file.read_text())
    except (json.JSONDecodeError, OSError):
        return runs

    entries = data if isinstance(data, list) else data.get("runs", [])
    for entry in entries:
        if not isinstance(entry, dict):
            continue

        task_ids = entry.get("task_ids", [])
        if not isinstance(task_ids, list):
            task_ids = [str(task_ids)] if task_ids else []

        runs.append(
            AgentRun(
                agent_type=entry.get("agent_type", "unknown"),
                project_slug=entry.get("project_slug", project_root.name),
                started_at=entry.get("started_at", ""),
                duration_ms=int(entry.get("duration_ms", 0)),
                total_tokens=int(entry.get("total_tokens", 0)),
                tool_uses=int(entry.get("tool_uses", 0)),
                status=entry.get("status", "unknown"),
                task_ids=[str(t) for t in task_ids],
            )
        )

    return runs


def aggregate_metrics(runs: list[AgentRun]) -> MetricsReport:
    """Aggregate a list of agent runs into a metrics report."""
    now = datetime.now(UTC).isoformat()

    if not runs:
        return MetricsReport(generated_at=now, total_runs=0)

    # Group by agent type
    by_agent: dict[str, list[AgentRun]] = {}
    by_project: dict[str, int] = {}

    for run in runs:
        by_agent.setdefault(run.agent_type, []).append(run)
        by_project[run.project_slug] = by_project.get(run.project_slug, 0) + 1

    agent_stats: dict[str, AgentStats] = {}
    for agent_type, agent_runs in by_agent.items():
        count = len(agent_runs)
        completed = sum(1 for r in agent_runs if r.status == "completed")
        agent_stats[agent_type] = AgentStats(
            runs=count,
            avg_duration_ms=sum(r.duration_ms for r in agent_runs) / count,
            avg_tokens=sum(r.total_tokens for r in agent_runs) / count,
            avg_tool_uses=sum(r.tool_uses for r in agent_runs) / count,
            success_rate=completed / count if count > 0 else 0.0,
        )

    return MetricsReport(
        generated_at=now,
        total_runs=len(runs),
        by_agent=agent_stats,
        by_project=by_project,
    )


def store_metrics(report: MetricsReport, db_path: Path) -> None:
    """Store a metrics report in DuckDB for trending."""
    from claude_cli.common.db import get_connection

    db_path.parent.mkdir(parents=True, exist_ok=True)

    with get_connection(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS metrics_reports (
                generated_at VARCHAR,
                total_runs INTEGER,
                report_json VARCHAR
            )
        """)
        conn.execute(
            "INSERT INTO metrics_reports VALUES (?, ?, ?)",
            [report.generated_at, report.total_runs, report.to_json()],
        )


def load_metrics_history(db_path: Path, days: int = 30) -> list[MetricsReport]:
    """Load historical metrics reports from DuckDB."""
    from claude_cli.common.db import get_connection

    if not db_path.exists():
        return []

    reports: list[MetricsReport] = []
    with get_connection(db_path) as conn:
        try:
            rows = conn.execute(
                "SELECT report_json FROM metrics_reports ORDER BY generated_at DESC LIMIT ?",
                [days],
            ).fetchall()
        except Exception:
            return []

        for (report_json,) in rows:
            try:
                data = json.loads(report_json)
                agent_stats = {}
                for name, stats in data.get("by_agent", {}).items():
                    agent_stats[name] = AgentStats(**stats)
                reports.append(
                    MetricsReport(
                        generated_at=data["generated_at"],
                        total_runs=data["total_runs"],
                        by_agent=agent_stats,
                        by_project=data.get("by_project", {}),
                    )
                )
            except (json.JSONDecodeError, KeyError, TypeError):
                continue

    return reports
