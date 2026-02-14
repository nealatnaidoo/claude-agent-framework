"""Portfolio-level cockpit aggregation.

Discovers governed projects and generates a portfolio dashboard HTML.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from string import Template

from claude_cli.cockpit.generator import collect_data, read_yaml_simple


def discover_projects(base_dir: Path | None = None) -> list[Path]:
    """Scan for projects with .claude/manifest.yaml.

    Discovery order:
    1. Registry: ~/.claude/devops/project_registry.yaml (if exists)
    2. Glob: base_dir/projects/*/.claude/manifest.yaml
    3. Glob: base_dir/*/.claude/manifest.yaml
    Deduplicates by resolved path.
    """
    seen: set[Path] = set()
    projects: list[Path] = []

    def _add(path: Path) -> None:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            projects.append(path)

    # 1. Registry
    registry_path = Path.home() / ".claude" / "devops" / "project_registry.yaml"
    if registry_path.exists():
        registry = read_yaml_simple(registry_path)
        registered = registry.get("projects", [])
        if isinstance(registered, list):
            for entry in registered:
                p = Path(entry) if isinstance(entry, str) else None
                if p and (p / ".claude" / "manifest.yaml").exists():
                    _add(p)

    if base_dir is None:
        base_dir = Path.home() / "Developer"

    # 2. base_dir/projects/*/.claude/manifest.yaml
    for manifest in sorted(base_dir.glob("projects/*/.claude/manifest.yaml")):
        _add(manifest.parent.parent)

    # 3. base_dir/*/.claude/manifest.yaml
    for manifest in sorted(base_dir.glob("*/.claude/manifest.yaml")):
        _add(manifest.parent)

    return projects


def collect_portfolio_data(projects: list[Path]) -> dict:
    """Aggregate data from all projects."""
    now = datetime.now(UTC).isoformat()
    totals = {"tasks_pending": 0, "tasks_completed": 0, "tasks_in_progress": 0, "tasks_blocked": 0}
    phase_distribution: dict[str, int] = {}
    project_summaries: list[dict] = []

    for project_root in projects:
        data = collect_data(project_root)
        phase = data.get("phase", "unknown")
        tasks = data.get("tasks", {})

        totals["tasks_pending"] += tasks.get("pending", 0)
        totals["tasks_completed"] += tasks.get("completed", 0)
        totals["tasks_in_progress"] += tasks.get("in_progress", 0)
        totals["tasks_blocked"] += tasks.get("blocked", 0)

        phase_distribution[phase] = phase_distribution.get(phase, 0) + 1

        gates = data.get("quality_gates")
        gates_result = gates.get("result", "unknown") if gates else "none"

        remediation_total = data.get("remediation", {}).get("total", 0)
        outbox_total = sum(data.get("outbox", {}).values())

        project_summaries.append({
            "slug": data.get("project_slug", project_root.name),
            "name": data.get("project_name", project_root.name),
            "phase": phase,
            "tasks": tasks,
            "gates_result": gates_result,
            "remediation_total": remediation_total,
            "outbox_total": outbox_total,
            "last_updated": data.get("last_updated", ""),
        })

    return {
        "portfolio_name": "Portfolio Cockpit",
        "generated_at": now,
        "project_count": len(projects),
        "projects": project_summaries,
        "totals": totals,
        "phase_distribution": phase_distribution,
    }


def render_portfolio_html(data: dict) -> str:
    """Render portfolio HTML using Template substitution."""
    from claude_cli.cockpit.docs_collector import collect_docs_data

    template_path = Path(__file__).parent / "templates" / "portfolio.html"
    template_str = template_path.read_text()

    docs_data = collect_docs_data()
    # Escape $ in docs JSON to avoid Template substitution conflicts
    docs_json = json.dumps(docs_data, indent=2, default=str).replace("$", "$$")

    template = Template(template_str)
    return template.safe_substitute(
        portfolio_data=json.dumps(data, indent=2, default=str),
        docs_data=docs_json,
        portfolio_name=data.get("portfolio_name", "Portfolio Cockpit"),
        generated_at=data.get("generated_at", ""),
    )


def generate_portfolio_cockpit(
    base_dir: Path | None = None, output: Path | None = None
) -> Path:
    """Generate portfolio cockpit. Returns path to HTML file."""
    projects = discover_projects(base_dir)
    data = collect_portfolio_data(projects)
    html = render_portfolio_html(data)

    if output is None:
        output = Path.home() / ".claude" / "portfolio_cockpit.html"

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html)
    return output
