"""Prime Directive compliance audit engine.

Full project audit combining manifest validation, artifact checks,
architecture analysis, governance status, and integration with
drift detection and pattern linting.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from claude_cli.cockpit.generator import read_yaml_simple


@dataclass
class AuditFinding:
    """A single audit finding."""

    category: str  # "manifest" | "artifacts" | "architecture" | "governance"
    rule_id: str  # "PA-001"
    severity: str  # "critical" | "high" | "medium" | "low"
    title: str
    detail: str
    file: str | None = None


@dataclass
class SectionResult:
    """Result for one audit section."""

    name: str
    passed: bool
    checks_run: int
    checks_passed: int


@dataclass
class AuditReport:
    """Full project audit report."""

    project_slug: str
    audited_at: str
    score: int  # 0-100
    grade: str  # A/B/C/D/F
    total_findings: int
    critical: int
    high: int
    medium: int
    low: int
    findings: list[AuditFinding] = field(default_factory=list)
    sections: dict[str, SectionResult] = field(default_factory=dict)

    def to_json(self) -> str:
        """Serialize report to JSON."""
        return json.dumps(
            {
                "project_slug": self.project_slug,
                "audited_at": self.audited_at,
                "score": self.score,
                "grade": self.grade,
                "total_findings": self.total_findings,
                "critical": self.critical,
                "high": self.high,
                "medium": self.medium,
                "low": self.low,
                "findings": [
                    {
                        "category": f.category,
                        "rule_id": f.rule_id,
                        "severity": f.severity,
                        "title": f.title,
                        "detail": f.detail,
                        "file": f.file,
                    }
                    for f in self.findings
                ],
                "sections": {
                    name: {
                        "name": s.name,
                        "passed": s.passed,
                        "checks_run": s.checks_run,
                        "checks_passed": s.checks_passed,
                    }
                    for name, s in self.sections.items()
                },
            },
            indent=2,
        )

    def to_markdown(self) -> str:
        """Serialize report to markdown."""
        lines = [
            f"# Audit Report: {self.project_slug}",
            "",
            f"**Audited at**: {self.audited_at}  ",
            f"**Score**: {self.score}/100 (Grade: {self.grade})  ",
            f"**Findings**: {self.total_findings} "
            f"(Critical: {self.critical}, High: {self.high}, "
            f"Medium: {self.medium}, Low: {self.low})",
            "",
        ]

        if self.sections:
            lines.append("## Sections")
            lines.append("")
            for name, section in self.sections.items():
                icon = "PASS" if section.passed else "FAIL"
                lines.append(
                    f"- [{icon}] **{section.name}**: "
                    f"{section.checks_passed}/{section.checks_run} passed"
                )
            lines.append("")

        if self.findings:
            lines.append("## Findings")
            lines.append("")
            for f in self.findings:
                lines.append(f"### {f.rule_id}: {f.title} [{f.severity}]")
                lines.append(f"- {f.detail}")
                if f.file:
                    lines.append(f"- File: `{f.file}`")
                lines.append("")

        if not self.findings:
            lines.append("No findings. Project is fully compliant.")
            lines.append("")

        return "\n".join(lines)


VALID_PHASES = {
    "init", "persona", "design", "ba", "coding", "qa", "review", "done",
}

VALID_TASK_STATUSES = {"pending", "in_progress", "completed", "blocked"}

REQUIRED_ARTIFACTS_BY_PHASE = {
    "coding": ["spec", "tasklist"],
    "qa": ["spec", "tasklist"],
    "review": ["spec", "tasklist"],
    "done": ["spec", "tasklist"],
}


def audit_manifest(project_root: Path) -> list[AuditFinding]:
    """Audit manifest.yaml for completeness and validity."""
    findings: list[AuditFinding] = []
    manifest_path = project_root / ".claude" / "manifest.yaml"

    # PA-001: manifest exists
    if not manifest_path.exists():
        findings.append(
            AuditFinding(
                category="manifest",
                rule_id="PA-001",
                severity="critical",
                title="Manifest missing",
                detail="No .claude/manifest.yaml found",
                file=".claude/manifest.yaml",
            )
        )
        return findings

    manifest = read_yaml_simple(manifest_path)

    # PA-002: schema_version present
    if not manifest.get("schema_version"):
        findings.append(
            AuditFinding(
                category="manifest",
                rule_id="PA-002",
                severity="high",
                title="Missing schema version",
                detail="manifest.yaml has no schema_version field",
                file=".claude/manifest.yaml",
            )
        )

    # PA-003: valid phase
    phase = manifest.get("phase", "")
    if phase and phase not in VALID_PHASES:
        findings.append(
            AuditFinding(
                category="manifest",
                rule_id="PA-003",
                severity="high",
                title="Invalid phase",
                detail=f"Phase '{phase}' not in valid set: {VALID_PHASES}",
                file=".claude/manifest.yaml",
            )
        )

    # PA-004: artifact files referenced in manifest exist
    artifact_versions = manifest.get("artifact_versions", {})
    if isinstance(artifact_versions, dict):
        for name, info in artifact_versions.items():
            if isinstance(info, dict):
                file_path = info.get("file", "")
                if file_path and not (project_root / file_path).exists():
                    findings.append(
                        AuditFinding(
                            category="manifest",
                            rule_id="PA-004",
                            severity="medium",
                            title="Referenced artifact missing",
                            detail=(
                                f"Artifact '{name}' references "
                                f"'{file_path}' which doesn't exist"
                            ),
                            file=file_path,
                        )
                    )

    # PA-005: valid task statuses
    outstanding = manifest.get("outstanding", {})
    if isinstance(outstanding, dict):
        tasks = outstanding.get("tasks", [])
        if isinstance(tasks, list):
            for task in tasks:
                if isinstance(task, dict):
                    status = task.get("status", "")
                    if status and status not in VALID_TASK_STATUSES:
                        task_id = task.get("id", "?")
                        findings.append(
                            AuditFinding(
                                category="manifest",
                                rule_id="PA-005",
                                severity="medium",
                                title="Invalid task status",
                                detail=f"Task '{task_id}' has invalid status '{status}'",
                                file=".claude/manifest.yaml",
                            )
                        )

    # PA-006: recently updated (within 7 days)
    last_updated = manifest.get("last_updated", "")
    if last_updated:
        try:
            updated_dt = datetime.fromisoformat(str(last_updated).replace("Z", "+00:00"))
            age_days = (datetime.now(UTC) - updated_dt).days
            if age_days > 7:
                findings.append(
                    AuditFinding(
                        category="manifest",
                        rule_id="PA-006",
                        severity="low",
                        title="Stale manifest",
                        detail=f"Manifest last updated {age_days} days ago",
                        file=".claude/manifest.yaml",
                    )
                )
        except (ValueError, TypeError):
            pass

    return findings


def audit_artifacts(project_root: Path) -> list[AuditFinding]:
    """Audit artifact structure and naming conventions."""
    findings: list[AuditFinding] = []
    claude_dir = project_root / ".claude"
    artifacts_dir = claude_dir / "artifacts"

    # Get current phase from manifest
    manifest = read_yaml_simple(claude_dir / "manifest.yaml")
    phase = manifest.get("phase", "unknown")

    # PA-010: required artifacts for phase
    required = REQUIRED_ARTIFACTS_BY_PHASE.get(phase, [])
    if required and artifacts_dir.exists():
        existing_files = [f.stem for f in artifacts_dir.iterdir() if f.is_file()]
        existing_names = " ".join(existing_files).lower()
        for artifact_type in required:
            if artifact_type not in existing_names:
                findings.append(
                    AuditFinding(
                        category="artifacts",
                        rule_id="PA-010",
                        severity="high",
                        title=f"Missing required artifact: {artifact_type}",
                        detail=f"Phase '{phase}' requires '{artifact_type}' artifact",
                        file=".claude/artifacts/",
                    )
                )
    elif required and not artifacts_dir.exists():
        findings.append(
            AuditFinding(
                category="artifacts",
                rule_id="PA-010",
                severity="high",
                title="Artifacts directory missing",
                detail=f"Phase '{phase}' requires artifacts but .claude/artifacts/ doesn't exist",
                file=".claude/artifacts/",
            )
        )

    # PA-011: naming convention (NNN_type_vM.ext)
    if artifacts_dir.exists():
        pattern = re.compile(r"^\d{3}_\w+_v\d+\.\w+$")
        for f in artifacts_dir.iterdir():
            if f.is_file() and not f.name.startswith("."):
                if not pattern.match(f.name):
                    findings.append(
                        AuditFinding(
                            category="artifacts",
                            rule_id="PA-011",
                            severity="low",
                            title="Non-standard artifact name",
                            detail=f"'{f.name}' doesn't match NNN_type_vM.ext convention",
                            file=f".claude/artifacts/{f.name}",
                        )
                    )

    # PA-012: evolution log exists
    if not (claude_dir / "evolution" / "evolution.md").exists():
        findings.append(
            AuditFinding(
                category="artifacts",
                rule_id="PA-012",
                severity="medium",
                title="Evolution log missing",
                detail="No .claude/evolution/evolution.md found",
                file=".claude/evolution/evolution.md",
            )
        )

    # PA-013: decisions log exists
    if not (claude_dir / "evolution" / "decisions.md").exists():
        findings.append(
            AuditFinding(
                category="artifacts",
                rule_id="PA-013",
                severity="medium",
                title="Decisions log missing",
                detail="No .claude/evolution/decisions.md found",
                file=".claude/evolution/decisions.md",
            )
        )

    return findings


def audit_architecture(project_root: Path) -> list[AuditFinding]:
    """Audit architecture for hexagonal compliance."""
    findings: list[AuditFinding] = []

    core_dir = project_root / "src" / "core"
    if not core_dir.exists():
        core_dir = project_root / "core"
    if not core_dir.exists():
        return findings  # No core directory to check

    for py_file in core_dir.rglob("*.py"):
        content = py_file.read_text()
        rel_path = str(py_file.relative_to(project_root))

        # PA-020: no adapter imports in core
        adapter_imports = [
            "requests", "httpx", "sqlalchemy", "flask", "fastapi", "django",
        ]
        for lib in adapter_imports:
            if re.search(rf"^\s*(import\s+{lib}|from\s+{lib})", content, re.MULTILINE):
                findings.append(
                    AuditFinding(
                        category="architecture",
                        rule_id="PA-020",
                        severity="high",
                        title=f"Adapter import in core: {lib}",
                        detail=f"Core module imports '{lib}' directly",
                        file=rel_path,
                    )
                )

        # PA-021: no datetime.now() in core
        if re.search(r"datetime\.now\(\)", content):
            findings.append(
                AuditFinding(
                    category="architecture",
                    rule_id="PA-021",
                    severity="medium",
                    title="Non-deterministic call in core",
                    detail="datetime.now() found in core; inject time via ports",
                    file=rel_path,
                )
            )

        # PA-022: no hardcoded secrets
        secret_patterns = [
            (r'(?:password|secret|api_key|token)\s*=\s*["\'][^"\']{8,}["\']', "hardcoded secret"),
        ]
        for pat, desc in secret_patterns:
            if re.search(pat, content, re.IGNORECASE):
                findings.append(
                    AuditFinding(
                        category="architecture",
                        rule_id="PA-022",
                        severity="critical",
                        title="Potential hardcoded secret",
                        detail=f"Possible {desc} found",
                        file=rel_path,
                    )
                )

    # PA-023: tests exist for services
    services_dir = core_dir / "services" if (core_dir / "services").exists() else core_dir
    service_files = list(services_dir.glob("*service*.py"))
    if service_files:
        tests_dir = project_root / "tests"
        if not tests_dir.exists():
            findings.append(
                AuditFinding(
                    category="architecture",
                    rule_id="PA-023",
                    severity="medium",
                    title="No tests directory",
                    detail="Services found but no tests/ directory exists",
                )
            )

    return findings


def audit_governance(project_root: Path) -> list[AuditFinding]:
    """Audit governance artifacts for freshness and completeness."""
    findings: list[AuditFinding] = []
    claude_dir = project_root / ".claude"

    # PA-030: remediation inbox not stale
    inbox_dir = claude_dir / "remediation" / "inbox"
    if inbox_dir.exists():
        inbox_files = list(inbox_dir.glob("*.md"))
        if len(inbox_files) > 5:
            findings.append(
                AuditFinding(
                    category="governance",
                    rule_id="PA-030",
                    severity="high",
                    title="Stale remediation inbox",
                    detail=f"{len(inbox_files)} unprocessed items in remediation inbox",
                    file=".claude/remediation/inbox/",
                )
            )

    # PA-031: quality gate evidence exists
    evidence_dir = claude_dir / "evidence"
    gates_file = evidence_dir / "quality_gates_run.json"
    if not gates_file.exists():
        findings.append(
            AuditFinding(
                category="governance",
                rule_id="PA-031",
                severity="medium",
                title="No quality gate evidence",
                detail="quality_gates_run.json not found in evidence/",
                file=".claude/evidence/quality_gates_run.json",
            )
        )

    # PA-032: outbox not stuck
    outbox_pending = claude_dir / "outbox" / "pending"
    if outbox_pending.exists():
        pending_files = list(outbox_pending.glob("*.md"))
        if len(pending_files) > 3:
            findings.append(
                AuditFinding(
                    category="governance",
                    rule_id="PA-032",
                    severity="medium",
                    title="Outbox backlog",
                    detail=f"{len(pending_files)} tasks stuck in outbox/pending",
                    file=".claude/outbox/pending/",
                )
            )

    return findings


def run_sub_audits(project_root: Path) -> list[AuditFinding]:
    """Run drift detection and pattern lint as sub-audits."""
    findings: list[AuditFinding] = []

    # Drift detection
    try:
        from claude_cli.drift.detector import detect_drift

        drift_report = detect_drift(project_root)
        if drift_report.has_drift:
            for check in drift_report.checks:
                if not check.passed:
                    findings.append(
                        AuditFinding(
                            category="governance",
                            rule_id="PA-040",
                            severity="medium",
                            title=f"Drift: {check.decision_id}",
                            detail=f"{check.assertion_desc}: {check.evidence}",
                        )
                    )
    except Exception:
        pass

    # Pattern lint
    try:
        from claude_cli.lint.checker import lint_project

        lint_report = lint_project(project_root)
        for violation in lint_report.violations:
            severity = "high" if violation.severity == "error" else "low"
            findings.append(
                AuditFinding(
                    category="governance",
                    rule_id="PA-050",
                    severity=severity,
                    title=f"Lint: {violation.rule_id}",
                    detail=violation.message,
                    file=violation.file,
                )
            )
    except Exception:
        pass

    return findings


def calculate_score(findings: list[AuditFinding]) -> tuple[int, str]:
    """Calculate audit score and grade from findings.

    Score = 100 - (critical*25 + high*10 + medium*3 + low*1)
    Grade: A (90+), B (75+), C (60+), D (40+), F (<40)
    """
    deductions = {
        "critical": 25,
        "high": 10,
        "medium": 3,
        "low": 1,
    }

    total_deduction = sum(
        deductions.get(f.severity, 0) for f in findings
    )
    score = max(0, 100 - total_deduction)

    if score >= 90:
        grade = "A"
    elif score >= 75:
        grade = "B"
    elif score >= 60:
        grade = "C"
    elif score >= 40:
        grade = "D"
    else:
        grade = "F"

    return score, grade


def _build_section(name: str, findings: list[AuditFinding], total_checks: int) -> SectionResult:
    """Build a SectionResult from findings."""
    failed = len(findings)
    passed = total_checks - failed
    return SectionResult(
        name=name,
        passed=failed == 0,
        checks_run=total_checks,
        checks_passed=max(0, passed),
    )


def audit_project(project_root: Path) -> AuditReport:
    """Run full project audit against Prime Directive."""
    all_findings: list[AuditFinding] = []
    sections: dict[str, SectionResult] = {}

    # Manifest audit
    manifest_findings = audit_manifest(project_root)
    all_findings.extend(manifest_findings)
    sections["manifest"] = _build_section("Manifest", manifest_findings, 6)

    # Artifacts audit
    artifact_findings = audit_artifacts(project_root)
    all_findings.extend(artifact_findings)
    sections["artifacts"] = _build_section("Artifacts", artifact_findings, 4)

    # Architecture audit
    arch_findings = audit_architecture(project_root)
    all_findings.extend(arch_findings)
    sections["architecture"] = _build_section("Architecture", arch_findings, 4)

    # Governance audit
    gov_findings = audit_governance(project_root)
    all_findings.extend(gov_findings)
    sections["governance"] = _build_section("Governance", gov_findings, 3)

    # Sub-audits (drift + lint)
    sub_findings = run_sub_audits(project_root)
    all_findings.extend(sub_findings)
    sections["sub_audits"] = _build_section("Sub-Audits", sub_findings, len(sub_findings) or 1)

    score, grade = calculate_score(all_findings)

    critical = sum(1 for f in all_findings if f.severity == "critical")
    high = sum(1 for f in all_findings if f.severity == "high")
    medium = sum(1 for f in all_findings if f.severity == "medium")
    low = sum(1 for f in all_findings if f.severity == "low")

    return AuditReport(
        project_slug=project_root.name,
        audited_at=datetime.now(UTC).isoformat(),
        score=score,
        grade=grade,
        total_findings=len(all_findings),
        critical=critical,
        high=high,
        medium=medium,
        low=low,
        findings=all_findings,
        sections=sections,
    )
