"""Pattern compliance linter for CI/CD and quality gate configs.

Validates project configurations against canonical patterns
defined in patterns/quality-gates/*.yaml.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from claude_cli.cockpit.generator import read_yaml_simple


@dataclass
class LintViolation:
    """A single lint rule violation."""

    rule_id: str
    severity: str  # "error" | "warning"
    message: str
    file: str
    suggestion: str


@dataclass
class LintReport:
    """Aggregated lint report for a project."""

    project_slug: str
    checked_at: str
    total: int
    errors: int
    warnings: int
    violations: list[LintViolation] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return self.errors > 0

    def to_json(self) -> str:
        """Serialize report to JSON."""
        return json.dumps(
            {
                "project_slug": self.project_slug,
                "checked_at": self.checked_at,
                "total": self.total,
                "errors": self.errors,
                "warnings": self.warnings,
                "has_errors": self.has_errors,
                "violations": [
                    {
                        "rule_id": v.rule_id,
                        "severity": v.severity,
                        "message": v.message,
                        "file": v.file,
                        "suggestion": v.suggestion,
                    }
                    for v in self.violations
                ],
            },
            indent=2,
        )

    def to_markdown(self) -> str:
        """Serialize report to markdown."""
        lines = [
            f"# Lint Report: {self.project_slug}",
            "",
            f"**Checked at**: {self.checked_at}  ",
            f"**Total**: {self.total} | **Errors**: {self.errors} | "
            f"**Warnings**: {self.warnings}",
            "",
        ]

        if not self.violations:
            lines.append("All checks passed.")
            return "\n".join(lines)

        for v in self.violations:
            icon = "ERROR" if v.severity == "error" else "WARN"
            lines.append(f"- [{icon}] **{v.rule_id}**: {v.message}")
            if v.file:
                lines.append(f"  - File: `{v.file}`")
            if v.suggestion:
                lines.append(f"  - Suggestion: {v.suggestion}")
            lines.append("")

        return "\n".join(lines)


# Rule definitions
RULES = {
    "PL-001": {
        "id": "PL-001",
        "severity": "error",
        "description": "Required gate commands present in pyproject.toml",
    },
    "PL-002": {
        "id": "PL-002",
        "severity": "warning",
        "description": "Evidence artifact paths match pattern spec",
    },
    "PL-003": {
        "id": "PL-003",
        "severity": "error",
        "description": "Determinism checks: forbidden patterns in core/",
    },
    "PL-004": {
        "id": "PL-004",
        "severity": "error",
        "description": "Hexagonal forbidden imports in core/",
    },
    "PL-005": {
        "id": "PL-005",
        "severity": "warning",
        "description": "Coverage thresholds configured",
    },
    "PL-010": {
        "id": "PL-010",
        "severity": "warning",
        "description": "CI config exists",
    },
    "PL-011": {
        "id": "PL-011",
        "severity": "warning",
        "description": "Required CI stages present",
    },
    "PL-012": {
        "id": "PL-012",
        "severity": "error",
        "description": "Deploy stage has manual gate",
    },
}


def load_canonical_pattern(pattern_name: str) -> dict:
    """Load a canonical quality gate pattern from the framework."""
    from claude_cli.common.config import get_framework_root

    root = get_framework_root()
    pattern_path = root / "patterns" / "quality-gates" / f"{pattern_name}.yaml"
    if pattern_path.exists():
        return read_yaml_simple(pattern_path)

    # Fallback: return default pattern
    return {
        "required_gate_commands": ["pytest", "ruff check"],
        "forbidden_core_imports": ["requests", "httpx", "sqlalchemy", "flask", "fastapi"],
        "forbidden_core_patterns": [r"datetime\.now\(\)", r"time\.time\(\)"],
        "required_ci_stages": ["test", "lint"],
        "evidence_paths": [".claude/evidence/quality_gates_run.json"],
    }


def detect_project_type(project_root: Path) -> str:
    """Detect project type from configuration files."""
    has_pyproject = (project_root / "pyproject.toml").exists()
    has_package_json = (project_root / "package.json").exists()

    if has_pyproject and has_package_json:
        return "fullstack"
    if has_pyproject:
        return "python"
    if has_package_json:
        return "frontend"
    return "unknown"


def check_quality_gates(project_root: Path, pattern: dict) -> list[LintViolation]:
    """Check quality gate configuration against canonical pattern."""
    violations: list[LintViolation] = []
    project_type = detect_project_type(project_root)

    # PL-001: Required gate commands in pyproject.toml
    if project_type in ("python", "fullstack"):
        pyproject_path = project_root / "pyproject.toml"
        if pyproject_path.exists():
            content = pyproject_path.read_text()
            required_commands = pattern.get("required_gate_commands", ["pytest", "ruff check"])
            for cmd in required_commands:
                if cmd not in content:
                    violations.append(
                        LintViolation(
                            rule_id="PL-001",
                            severity="error",
                            message=f"Required gate command '{cmd}' not found in pyproject.toml",
                            file="pyproject.toml",
                            suggestion=f"Add '{cmd}' to [tool.pytest] or [project.scripts]",
                        )
                    )

    # PL-002: Evidence artifact paths exist
    evidence_paths = pattern.get("evidence_paths", [".claude/evidence/quality_gates_run.json"])
    for ep in evidence_paths:
        if not (project_root / ep).exists():
            violations.append(
                LintViolation(
                    rule_id="PL-002",
                    severity="warning",
                    message=f"Evidence artifact not found: {ep}",
                    file=ep,
                    suggestion="Run quality gates to generate evidence artifacts",
                )
            )

    # PL-003: Determinism checks - forbidden patterns in core/
    core_dir = project_root / "src" / "core"
    if not core_dir.exists():
        core_dir = project_root / "core"

    if core_dir.exists():
        forbidden_patterns = pattern.get(
            "forbidden_core_patterns", [r"datetime\.now\(\)", r"time\.time\(\)"]
        )
        for py_file in core_dir.rglob("*.py"):
            content = py_file.read_text()
            for fp in forbidden_patterns:
                if re.search(fp, content):
                    rel_path = str(py_file.relative_to(project_root))
                    violations.append(
                        LintViolation(
                            rule_id="PL-003",
                            severity="error",
                            message=f"Non-deterministic pattern '{fp}' found in core",
                            file=rel_path,
                            suggestion="Inject time via ports/dependencies instead",
                        )
                    )

    # PL-004: Hexagonal forbidden imports in core/
    if core_dir.exists():
        forbidden_imports = pattern.get(
            "forbidden_core_imports",
            ["requests", "httpx", "sqlalchemy", "flask", "fastapi"],
        )
        for py_file in core_dir.rglob("*.py"):
            content = py_file.read_text()
            for lib in forbidden_imports:
                if re.search(rf"^\s*(import\s+{lib}|from\s+{lib})", content, re.MULTILINE):
                    rel_path = str(py_file.relative_to(project_root))
                    violations.append(
                        LintViolation(
                            rule_id="PL-004",
                            severity="error",
                            message=f"Forbidden import '{lib}' in core module",
                            file=rel_path,
                            suggestion=f"Move '{lib}' usage to adapters layer",
                        )
                    )

    # PL-005: Coverage thresholds
    if project_type in ("python", "fullstack"):
        pyproject_path = project_root / "pyproject.toml"
        if pyproject_path.exists():
            content = pyproject_path.read_text()
            if "fail_under" not in content and "coverage" not in content.lower():
                violations.append(
                    LintViolation(
                        rule_id="PL-005",
                        severity="warning",
                        message="No coverage threshold configured",
                        file="pyproject.toml",
                        suggestion="Add [tool.coverage.report] fail_under = 80",
                    )
                )

    return violations


def check_ci_config(project_root: Path) -> list[LintViolation]:
    """Check CI/CD configuration for required elements."""
    violations: list[LintViolation] = []

    # PL-010: CI config exists
    ci_files = [
        ".gitlab-ci.yml",
        ".github/workflows",
        "Jenkinsfile",
        ".circleci/config.yml",
    ]
    ci_found = False
    ci_file = ""
    for cf in ci_files:
        path = project_root / cf
        if path.exists():
            ci_found = True
            ci_file = cf
            break

    if not ci_found:
        violations.append(
            LintViolation(
                rule_id="PL-010",
                severity="warning",
                message="No CI configuration found",
                file="",
                suggestion="Add .gitlab-ci.yml or .github/workflows/",
            )
        )
        return violations  # Can't check stages without CI config

    # PL-011: Required CI stages
    ci_content = ""
    ci_path = project_root / ci_file
    if ci_path.is_file():
        ci_content = ci_path.read_text()
    elif ci_path.is_dir():
        # GitHub workflows directory
        for wf in ci_path.glob("*.yml"):
            ci_content += wf.read_text() + "\n"
        for wf in ci_path.glob("*.yaml"):
            ci_content += wf.read_text() + "\n"

    required_stages = ["test", "lint"]
    for stage in required_stages:
        if stage not in ci_content.lower():
            violations.append(
                LintViolation(
                    rule_id="PL-011",
                    severity="warning",
                    message=f"Required CI stage '{stage}' not found",
                    file=ci_file,
                    suggestion=f"Add a '{stage}' stage to CI configuration",
                )
            )

    # PL-012: Deploy stage has manual gate
    if "deploy" in ci_content.lower():
        has_manual = any(
            kw in ci_content.lower()
            for kw in ["when: manual", "workflow_dispatch", "environment:", "manual"]
        )
        if not has_manual:
            violations.append(
                LintViolation(
                    rule_id="PL-012",
                    severity="error",
                    message="Deploy stage lacks manual approval gate",
                    file=ci_file,
                    suggestion="Add 'when: manual' or environment protection rules",
                )
            )

    return violations


def lint_project(project_root: Path) -> LintReport:
    """Run all lint checks against a project."""
    project_type = detect_project_type(project_root)
    pattern = load_canonical_pattern(project_type)

    violations: list[LintViolation] = []
    violations.extend(check_quality_gates(project_root, pattern))
    violations.extend(check_ci_config(project_root))

    errors = sum(1 for v in violations if v.severity == "error")
    warnings = sum(1 for v in violations if v.severity == "warning")

    return LintReport(
        project_slug=project_root.name,
        checked_at=datetime.now(UTC).isoformat(),
        total=len(violations),
        errors=errors,
        warnings=warnings,
        violations=violations,
    )
