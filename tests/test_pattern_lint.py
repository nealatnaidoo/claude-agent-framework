"""Tests for pattern compliance linter."""

import json

import pytest

from claude_cli.lint.checker import (
    LintReport,
    LintViolation,
    check_ci_config,
    check_quality_gates,
    detect_project_type,
    lint_project,
)


@pytest.fixture
def python_project(tmp_path):
    """Create a compliant Python project structure."""
    (tmp_path / "pyproject.toml").write_text("""\
[project]
name = "test"

[tool.pytest.ini_options]
testpaths = ["tests"]

[project.scripts]
test = "pytest"
lint = "ruff check"

[tool.coverage.report]
fail_under = 80
""")
    core_dir = tmp_path / "src" / "core"
    core_dir.mkdir(parents=True)
    (core_dir / "service.py").write_text("class UserService:\n    pass\n")

    # CI config
    (tmp_path / ".gitlab-ci.yml").write_text("""\
stages:
  - test
  - lint
  - deploy

test:
  stage: test
  script: pytest

lint:
  stage: lint
  script: ruff check

deploy:
  stage: deploy
  when: manual
  script: deploy.sh
""")

    # Evidence
    evidence_dir = tmp_path / ".claude" / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "quality_gates_run.json").write_text("{}")

    return tmp_path


@pytest.fixture
def frontend_project(tmp_path):
    """Create a frontend project structure."""
    (tmp_path / "package.json").write_text('{"name": "test-app"}')
    return tmp_path


class TestDetectProjectType:
    def test_python_project(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("")
        assert detect_project_type(tmp_path) == "python"

    def test_frontend_project(self, tmp_path):
        (tmp_path / "package.json").write_text("{}")
        assert detect_project_type(tmp_path) == "frontend"

    def test_fullstack_project(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("")
        (tmp_path / "package.json").write_text("{}")
        assert detect_project_type(tmp_path) == "fullstack"

    def test_unknown_project(self, tmp_path):
        assert detect_project_type(tmp_path) == "unknown"


class TestCheckQualityGates:
    def test_compliant_project(self, python_project):
        pattern = {
            "required_gate_commands": ["pytest", "ruff check"],
            "evidence_paths": [".claude/evidence/quality_gates_run.json"],
            "forbidden_core_patterns": [r"datetime\.now\(\)"],
            "forbidden_core_imports": ["requests"],
        }
        violations = check_quality_gates(python_project, pattern)
        assert len(violations) == 0

    def test_missing_gate_command(self, python_project):
        pattern = {
            "required_gate_commands": ["pytest", "mypy"],
            "evidence_paths": [],
            "forbidden_core_patterns": [],
            "forbidden_core_imports": [],
        }
        violations = check_quality_gates(python_project, pattern)
        pl001 = [v for v in violations if v.rule_id == "PL-001"]
        assert len(pl001) == 1
        assert "mypy" in pl001[0].message

    def test_missing_evidence(self, python_project):
        pattern = {
            "required_gate_commands": [],
            "evidence_paths": [".claude/evidence/nonexistent.json"],
            "forbidden_core_patterns": [],
            "forbidden_core_imports": [],
        }
        violations = check_quality_gates(python_project, pattern)
        pl002 = [v for v in violations if v.rule_id == "PL-002"]
        assert len(pl002) == 1

    def test_nondeterministic_pattern(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n")
        core_dir = tmp_path / "src" / "core"
        core_dir.mkdir(parents=True)
        (core_dir / "service.py").write_text("from datetime import datetime\nnow = datetime.now()\n")

        pattern = {
            "required_gate_commands": [],
            "evidence_paths": [],
            "forbidden_core_patterns": [r"datetime\.now\(\)"],
            "forbidden_core_imports": [],
        }
        violations = check_quality_gates(tmp_path, pattern)
        pl003 = [v for v in violations if v.rule_id == "PL-003"]
        assert len(pl003) == 1

    def test_forbidden_import_in_core(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n")
        core_dir = tmp_path / "src" / "core"
        core_dir.mkdir(parents=True)
        (core_dir / "bad.py").write_text("import requests\n")

        pattern = {
            "required_gate_commands": [],
            "evidence_paths": [],
            "forbidden_core_patterns": [],
            "forbidden_core_imports": ["requests"],
        }
        violations = check_quality_gates(tmp_path, pattern)
        pl004 = [v for v in violations if v.rule_id == "PL-004"]
        assert len(pl004) == 1

    def test_no_coverage_threshold(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n")

        pattern = {
            "required_gate_commands": [],
            "evidence_paths": [],
            "forbidden_core_patterns": [],
            "forbidden_core_imports": [],
        }
        violations = check_quality_gates(tmp_path, pattern)
        pl005 = [v for v in violations if v.rule_id == "PL-005"]
        assert len(pl005) == 1


class TestCheckCIConfig:
    def test_no_ci_config(self, tmp_path):
        violations = check_ci_config(tmp_path)
        assert len(violations) == 1
        assert violations[0].rule_id == "PL-010"

    def test_complete_ci(self, python_project):
        violations = check_ci_config(python_project)
        assert len(violations) == 0

    def test_missing_stage(self, tmp_path):
        (tmp_path / ".gitlab-ci.yml").write_text("stages:\n  - build\n")
        violations = check_ci_config(tmp_path)
        pl011 = [v for v in violations if v.rule_id == "PL-011"]
        assert len(pl011) == 2  # missing test and lint

    def test_deploy_without_gate(self, tmp_path):
        (tmp_path / ".gitlab-ci.yml").write_text(
            "stages:\n  - test\n  - lint\n  - deploy\n\n"
            "deploy:\n  script: deploy.sh\n"
        )
        violations = check_ci_config(tmp_path)
        pl012 = [v for v in violations if v.rule_id == "PL-012"]
        assert len(pl012) == 1

    def test_github_workflows(self, tmp_path):
        wf_dir = tmp_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        (wf_dir / "ci.yml").write_text("name: CI\njobs:\n  test:\n  lint:\n")
        violations = check_ci_config(tmp_path)
        assert not any(v.rule_id == "PL-010" for v in violations)


class TestLintProject:
    def test_compliant_project(self, python_project):
        report = lint_project(python_project)
        assert report.errors == 0
        assert report.has_errors is False

    def test_violations_detected(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n")
        core_dir = tmp_path / "src" / "core"
        core_dir.mkdir(parents=True)
        (core_dir / "bad.py").write_text("import requests\nfrom datetime import datetime\nnow = datetime.now()\n")

        report = lint_project(tmp_path)
        assert report.errors > 0
        assert report.has_errors is True
        assert report.project_slug == tmp_path.name


class TestLintReportSerialization:
    def test_to_json(self, python_project):
        report = lint_project(python_project)
        data = json.loads(report.to_json())
        assert "project_slug" in data
        assert "violations" in data
        assert isinstance(data["has_errors"], bool)

    def test_to_markdown(self, python_project):
        report = lint_project(python_project)
        md = report.to_markdown()
        assert "# Lint Report:" in md

    def test_clean_report_markdown(self, python_project):
        report = lint_project(python_project)
        md = report.to_markdown()
        assert "All checks passed" in md

    def test_violations_markdown(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n")
        core_dir = tmp_path / "src" / "core"
        core_dir.mkdir(parents=True)
        (core_dir / "bad.py").write_text("import requests\n")

        report = lint_project(tmp_path)
        md = report.to_markdown()
        assert "PL-004" in md
        assert "ERROR" in md
