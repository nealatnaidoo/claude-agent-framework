"""Tests for the batch CLI commands."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from typer.testing import CliRunner

from claude_cli.batch.cli import app
from claude_cli.batch.ledger import create_ledger


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def project_dir(tmp_path):
    """Create a minimal project with source files."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    (claude_dir / "manifest.yaml").write_text("phase: coding\n")

    src = tmp_path / "src"
    src.mkdir()
    (src / "auth.py").write_text("# auth")
    (src / "api.py").write_text("# api")
    return tmp_path


@pytest.fixture
def batch_with_ledger(project_dir):
    """Create a project with an initialized batch."""
    bd = project_dir / ".claude" / "batch" / "test-batch-001"
    items = ["src/auth.py", "src/api.py"]
    create_ledger("test-batch-001", items, "Review $item", {"pattern": "src/*.py", "parallel": 2}, bd)
    return project_dir


class TestInitCommand:
    def test_init_creates_ledger(self, runner, project_dir):
        with patch("claude_cli.batch.cli._find_project_root", return_value=project_dir):
            result = runner.invoke(app, [
                "init",
                "--pattern", "src/*.py",
                "--prompt", "Review $item for issues",
            ])
        assert result.exit_code == 0
        assert "Batch initialized" in result.output
        assert "Items: 2" in result.output

    def test_init_no_matches(self, runner, project_dir):
        with patch("claude_cli.batch.cli._find_project_root", return_value=project_dir):
            result = runner.invoke(app, [
                "init",
                "--pattern", "*.rs",
                "--prompt", "Review $item",
            ])
        assert result.exit_code == 1
        assert "No items match" in result.output

    def test_init_no_project(self, runner):
        with patch("claude_cli.batch.cli._find_project_root", return_value=None):
            result = runner.invoke(app, [
                "init",
                "--pattern", "*.py",
                "--prompt", "Review $item",
            ])
        assert result.exit_code == 1
        assert "No .claude/manifest.yaml" in result.output

    def test_init_with_options(self, runner, project_dir):
        with patch("claude_cli.batch.cli._find_project_root", return_value=project_dir):
            result = runner.invoke(app, [
                "init",
                "--pattern", "src/*.py",
                "--prompt", "Check $item",
                "--parallel", "3",
                "--max-turns", "30",
                "--allowed-tools", "Read,Grep,Glob",
            ])
        assert result.exit_code == 0
        assert "Parallel: 3" in result.output


class TestStatusCommand:
    def test_status_shows_counts(self, runner, batch_with_ledger):
        with patch("claude_cli.batch.cli._find_project_root", return_value=batch_with_ledger):
            result = runner.invoke(app, [
                "status",
                "--batch-id", "test-batch-001",
            ])
        assert result.exit_code == 0
        assert "test-batch-001" in result.output

    def test_status_not_found(self, runner, project_dir):
        with patch("claude_cli.batch.cli._find_project_root", return_value=project_dir):
            result = runner.invoke(app, [
                "status",
                "--batch-id", "nonexistent",
            ])
        assert result.exit_code == 1
        assert "not found" in result.output


class TestReportCommand:
    def test_report_produces_output(self, runner, batch_with_ledger):
        with patch("claude_cli.batch.cli._find_project_root", return_value=batch_with_ledger):
            result = runner.invoke(app, [
                "report",
                "--batch-id", "test-batch-001",
            ])
        assert result.exit_code == 0
        assert "Batch Report" in result.output

    def test_report_saves_file(self, runner, batch_with_ledger):
        with patch("claude_cli.batch.cli._find_project_root", return_value=batch_with_ledger):
            runner.invoke(app, ["report", "--batch-id", "test-batch-001"])
        report_path = batch_with_ledger / ".claude" / "batch" / "test-batch-001" / "report.md"
        assert report_path.exists()


class TestRunCommand:
    def test_run_no_claude(self, runner, batch_with_ledger):
        with patch("claude_cli.batch.cli._find_project_root", return_value=batch_with_ledger):
            with patch("claude_cli.batch.orchestrator.shutil.which", return_value=None):
                result = runner.invoke(app, [
                    "run",
                    "--batch-id", "test-batch-001",
                ])
        assert result.exit_code == 1
        assert "claude CLI not found" in result.output

    def test_run_not_found(self, runner, project_dir):
        with patch("claude_cli.batch.cli._find_project_root", return_value=project_dir):
            result = runner.invoke(app, [
                "run",
                "--batch-id", "nonexistent",
            ])
        assert result.exit_code == 1
        assert "not found" in result.output
