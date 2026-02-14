"""
Cockpit HTML dashboard generator.

Reads project .claude/ data and produces a self-contained HTML dashboard
with a dark executive theme. No external dependencies.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from string import Template


def find_project_root(start: Path | None = None) -> Path | None:
    """Walk up from start (or cwd) to find .claude/manifest.yaml."""
    current = start or Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".claude" / "manifest.yaml").exists():
            return parent
        if parent == Path.home():
            break
    return None


def read_yaml_simple(path: Path) -> dict:
    """Read YAML using PyYAML if available, else basic parser."""
    if not path.exists():
        return {}
    try:
        import yaml

        return yaml.safe_load(path.read_text()) or {}
    except ImportError:
        # Minimal fallback: extract top-level key: value pairs
        result = {}
        for line in path.read_text().splitlines():
            if ":" in line and not line.startswith(" ") and not line.startswith("#"):
                key, _, value = line.partition(":")
                result[key.strip()] = value.strip().strip("\"'")
        return result


def collect_data(project_root: Path) -> dict:
    """Collect all cockpit data from project sources."""
    claude_dir = project_root / ".claude"
    data: dict = {
        "project_slug": project_root.name,
        "project_name": project_root.name.replace("-", " ").replace("_", " ").title(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": "unknown",
        "phase_started": None,
        "last_updated": None,
        "tasks": {"pending": 0, "in_progress": 0, "completed": 0, "blocked": 0},
        "quality_gates": None,
        "remediation": {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0},
        "outbox": {"pending": 0, "active": 0, "completed": 0, "rejected": 0},
        "commits": [],
        "artifacts": {},
    }

    # Read manifest
    manifest = read_yaml_simple(claude_dir / "manifest.yaml")
    if manifest:
        data["project_slug"] = manifest.get("project_slug", data["project_slug"])
        data["project_name"] = manifest.get("project_name", data["project_name"])
        data["phase"] = manifest.get("phase", "unknown")
        data["phase_started"] = manifest.get("phase_started")
        data["last_updated"] = manifest.get("last_updated")

        # Count tasks by status
        tasks = manifest.get("outstanding", {})
        if isinstance(tasks, dict):
            task_list = tasks.get("tasks", [])
            if isinstance(task_list, list):
                for task in task_list:
                    if isinstance(task, dict):
                        status = task.get("status", "pending")
                        blocked_by = task.get("blocked_by", [])
                        if blocked_by and status == "pending":
                            data["tasks"]["blocked"] += 1
                        elif status in data["tasks"]:
                            data["tasks"][status] += 1

            # Count remediation
            rem_list = tasks.get("remediation", [])
            if isinstance(rem_list, list):
                data["remediation"]["total"] = len(rem_list)
                for item in rem_list:
                    if isinstance(item, dict):
                        sev = item.get("priority", item.get("severity", "medium"))
                        if sev in data["remediation"]:
                            data["remediation"][sev] += 1

        # Artifact versions
        av = manifest.get("artifact_versions", {})
        if isinstance(av, dict):
            for name, info in av.items():
                if isinstance(info, dict):
                    data["artifacts"][name] = {
                        "version": info.get("version", "?"),
                        "file": info.get("file", ""),
                    }
                else:
                    data["artifacts"][name] = {"version": str(info), "file": ""}

    # Quality gates evidence
    gates_file = claude_dir / "evidence" / "quality_gates_run.json"
    if gates_file.exists():
        try:
            gates = json.loads(gates_file.read_text())
            data["quality_gates"] = {
                "result": gates.get("result", gates.get("overall", "unknown")),
                "timestamp": gates.get("timestamp", gates.get("run_at", "")),
                "gates": gates.get("gates", gates.get("checks", [])),
            }
        except (json.JSONDecodeError, KeyError):
            pass

    # Remediation inbox count
    inbox_dir = claude_dir / "remediation" / "inbox"
    if inbox_dir.exists():
        inbox_files = list(inbox_dir.glob("*.md"))
        if inbox_files:
            data["remediation"]["total"] = max(
                data["remediation"]["total"], len(inbox_files)
            )

    # Outbox counts
    for status in ("pending", "active", "completed", "rejected"):
        outbox_dir = claude_dir / "outbox" / status
        if outbox_dir.exists():
            data["outbox"][status] = len(list(outbox_dir.glob("*.md")))

    # Recent commits
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-20", "--format=%h|%s|%ai"],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=5,
        )
        if result.returncode == 0:
            for line in result.stdout.strip().splitlines():
                parts = line.split("|", 2)
                if len(parts) == 3:
                    data["commits"].append(
                        {"hash": parts[0], "message": parts[1], "date": parts[2]}
                    )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return data


def render_html(data: dict) -> str:
    """Render cockpit data as self-contained HTML."""
    from claude_cli.cockpit.docs_collector import collect_docs_data

    template_path = Path(__file__).parent / "templates" / "project.html"
    if template_path.exists():
        template_str = template_path.read_text()
    else:
        template_str = _default_template()

    docs_data = collect_docs_data()
    # Escape $ in docs JSON to avoid Template substitution conflicts
    docs_json = json.dumps(docs_data, indent=2, default=str).replace("$", "$$")

    template = Template(template_str)
    return template.safe_substitute(
        cockpit_data=json.dumps(data, indent=2, default=str),
        docs_data=docs_json,
        project_name=data.get("project_name", "Project"),
        generated_at=data.get("generated_at", ""),
    )


def generate_cockpit(
    project_root: Path | None = None, output: Path | None = None
) -> Path:
    """Generate cockpit HTML for a project. Returns path to the HTML file."""
    if project_root is None:
        project_root = find_project_root()
    if project_root is None:
        raise FileNotFoundError("No .claude/manifest.yaml found in any parent directory")

    data = collect_data(project_root)
    html = render_html(data)

    if output is None:
        output = project_root / ".claude" / "cockpit.html"

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html)
    return output


def main():
    """CLI entry point."""
    import sys

    try:
        path = generate_cockpit()
        print(f"Cockpit generated: {path}")
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
