"""Decisions-vs-code drift detection engine.

Reads verifiable assertions from {project}/.claude/drift_rules.yaml
and checks them against the actual codebase.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from claude_cli.cockpit.generator import read_yaml_simple


@dataclass
class DriftCheck:
    """Result of a single drift assertion check."""

    decision_id: str
    title: str
    assertion_desc: str
    assertion_type: str
    passed: bool
    evidence: str


@dataclass
class DriftReport:
    """Aggregated drift detection report for a project."""

    project_slug: str
    checked_at: str
    total: int
    passed: int
    failed: int
    skipped: int
    checks: list[DriftCheck] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        return self.failed > 0

    def to_json(self) -> str:
        return json.dumps(
            {
                "project_slug": self.project_slug,
                "checked_at": self.checked_at,
                "total": self.total,
                "passed": self.passed,
                "failed": self.failed,
                "skipped": self.skipped,
                "has_drift": self.has_drift,
                "checks": [
                    {
                        "decision_id": c.decision_id,
                        "title": c.title,
                        "assertion_desc": c.assertion_desc,
                        "assertion_type": c.assertion_type,
                        "passed": c.passed,
                        "evidence": c.evidence,
                    }
                    for c in self.checks
                ],
            },
            indent=2,
        )

    def to_markdown(self) -> str:
        lines = [
            f"# Drift Report: {self.project_slug}",
            "",
            f"**Checked at**: {self.checked_at}  ",
            f"**Total**: {self.total} | **Passed**: {self.passed} | "
            f"**Failed**: {self.failed} | **Skipped**: {self.skipped}",
            "",
        ]
        if not self.checks:
            lines.append("No drift rules configured.")
            return "\n".join(lines)

        current_decision = ""
        for check in self.checks:
            if check.decision_id != current_decision:
                current_decision = check.decision_id
                lines.append(f"## {check.decision_id}: {check.title}")
                lines.append("")
            icon = "PASS" if check.passed else "FAIL"
            lines.append(f"- [{icon}] {check.assertion_desc}")
            if not check.passed:
                lines.append(f"  - Evidence: {check.evidence}")
            lines.append("")

        return "\n".join(lines)


def load_drift_rules(rules_path: Path) -> list[dict]:
    """Load drift rules from a YAML file."""
    data = read_yaml_simple(rules_path)
    if not data:
        return []
    rules = data.get("rules", [])
    if not isinstance(rules, list):
        return []
    return rules


def run_check(rule: dict, project_root: Path) -> list[DriftCheck]:
    """Run all assertions for a single decision rule. Returns list of DriftCheck."""
    decision_id = rule.get("decision_id", "UNKNOWN")
    title = rule.get("title", "Untitled")
    assertions = rule.get("assertions", [])
    results: list[DriftCheck] = []

    for assertion in assertions:
        if not isinstance(assertion, dict):
            continue

        atype = assertion.get("type", "")
        apath = assertion.get("path", "")
        pattern = assertion.get("pattern", "")
        desc = assertion.get("description", f"{atype} check")
        target = project_root / apath

        if atype == "file_exists":
            passed = target.exists()
            evidence = f"Path {'exists' if passed else 'not found'}: {apath}"

        elif atype == "file_absent":
            passed = not target.exists()
            evidence = f"Path {'not found (good)' if passed else 'exists (unexpected)'}: {apath}"

        elif atype == "grep_exists":
            passed, evidence = _run_grep(pattern, target, expect_match=True)

        elif atype == "grep_absent":
            passed, evidence = _run_grep(pattern, target, expect_match=False)

        else:
            passed = False
            evidence = f"Unknown assertion type: {atype}"

        results.append(
            DriftCheck(
                decision_id=decision_id,
                title=title,
                assertion_desc=desc,
                assertion_type=atype,
                passed=passed,
                evidence=evidence,
            )
        )

    return results


def _run_grep(pattern: str, target: Path, *, expect_match: bool) -> tuple[bool, str]:
    """Run grep and return (passed, evidence)."""
    if not target.exists():
        if expect_match:
            return False, f"Path not found: {target}"
        return True, f"Path not found (nothing to match): {target}"

    try:
        args = ["grep", "-r", "-l", pattern]
        if target.is_file():
            args.append(str(target))
        else:
            args.append(str(target))

        result = subprocess.run(
            args, capture_output=True, text=True, timeout=10
        )
        has_match = result.returncode == 0 and result.stdout.strip() != ""

        if expect_match:
            if has_match:
                files = result.stdout.strip().splitlines()[:3]
                return True, f"Pattern found in: {', '.join(files)}"
            return False, f"Pattern '{pattern}' not found in {target}"
        else:
            if has_match:
                files = result.stdout.strip().splitlines()[:3]
                return False, f"Pattern '{pattern}' found (unexpected) in: {', '.join(files)}"
            return True, f"Pattern '{pattern}' absent from {target}"

    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return False, f"Grep error: {e}"


def detect_drift(project_root: Path) -> DriftReport:
    """Run full drift detection for a project."""
    rules_path = project_root / ".claude" / "drift_rules.yaml"
    rules = load_drift_rules(rules_path)

    checks: list[DriftCheck] = []
    for rule in rules:
        checks.extend(run_check(rule, project_root))

    passed = sum(1 for c in checks if c.passed)
    failed = sum(1 for c in checks if not c.passed)

    return DriftReport(
        project_slug=project_root.name,
        checked_at=datetime.now(UTC).isoformat(),
        total=len(checks),
        passed=passed,
        failed=failed,
        skipped=0,
        checks=checks,
    )


_RULES_TEMPLATE = """\
schema_version: "1.0"
rules:
  - decision_id: "ADR-001"
    title: "Example: Hexagonal Architecture"
    assertions:
      - type: "file_exists"
        path: "src/core/"
        description: "Core domain directory exists"
      - type: "grep_absent"
        pattern: "import requests"
        path: "src/core/"
        description: "Core domain has no direct HTTP calls"

  # Add more decisions below:
  # - decision_id: "ADR-002"
  #   title: "Config-Driven Scoring"
  #   assertions:
  #     - type: "file_exists"
  #       path: "config/scoring/"
  #       description: "Scoring config directory exists"
"""


def create_rules_template(project_root: Path) -> Path:
    """Create a drift_rules.yaml template in the project's .claude/ directory."""
    rules_path = project_root / ".claude" / "drift_rules.yaml"
    rules_path.parent.mkdir(parents=True, exist_ok=True)
    rules_path.write_text(_RULES_TEMPLATE)
    return rules_path
