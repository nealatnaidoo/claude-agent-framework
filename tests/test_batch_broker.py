"""Tests for the batch results broker module."""

import json
from pathlib import Path

import pytest
import yaml

from claude_cli.batch.broker import (
    collect_summaries,
    generate_report,
    read_result,
    sanitize_item_name,
    write_result,
)
from claude_cli.batch.ledger import create_ledger, update_item_status


@pytest.fixture
def results_dir(tmp_path):
    """Create a temporary results directory."""
    rd = tmp_path / "results"
    rd.mkdir()
    return rd


@pytest.fixture
def batch_dir(tmp_path):
    """Create a batch with ledger and some results."""
    bd = tmp_path / ".claude" / "batch" / "test-batch"
    items = ["src/foo.py", "src/bar.py", "src/baz.py"]
    create_ledger("test-batch", items, "Review $item", {"pattern": "src/*.py"}, bd)

    # Mark first as done with a result
    update_item_status(bd / "ledger.yaml", "src/foo.py", "done",
                       result_summary="2 issues", exit_code=0)
    # Mark second as failed
    update_item_status(bd / "ledger.yaml", "src/bar.py", "failed",
                       result_summary="Timeout", exit_code=1)

    # Write result files
    results = bd / "results"
    (results / "src_foo_py.json").write_text(json.dumps({
        "schema_version": "1.0",
        "item": "src/foo.py",
        "exit_code": 0,
        "summary": "2 issues found",
        "completed_at": "2026-02-14T14:32:00Z",
    }))
    (results / "src_bar_py.json").write_text(json.dumps({
        "schema_version": "1.0",
        "item": "src/bar.py",
        "exit_code": 1,
        "summary": "Timeout after 20 turns",
        "completed_at": "2026-02-14T14:33:00Z",
    }))

    return bd


class TestSanitizeItemName:
    def test_basic(self):
        assert sanitize_item_name("src/auth/service.py") == "src_auth_service_py"

    def test_no_slashes(self):
        assert sanitize_item_name("file.py") == "file_py"

    def test_deep_nesting(self):
        assert sanitize_item_name("a/b/c/d/e.txt") == "a_b_c_d_e_txt"

    def test_yaml_extension(self):
        assert sanitize_item_name("config.yaml") == "config_yaml"

    def test_no_trailing_underscore(self):
        # Path ending with / shouldn't produce trailing _
        result = sanitize_item_name("src/")
        assert not result.endswith("_")


class TestWriteResult:
    def test_writes_json_file(self, results_dir):
        path = write_result(results_dir, "src/foo.py", {
            "exit_code": 0,
            "summary": "OK",
        })
        assert path.exists()
        assert path.name == "src_foo_py.json"

    def test_result_has_metadata(self, results_dir):
        write_result(results_dir, "src/foo.py", {"exit_code": 0})
        data = json.loads((results_dir / "src_foo_py.json").read_text())
        assert data["schema_version"] == "1.0"
        assert data["item"] == "src/foo.py"
        assert "written_at" in data

    def test_creates_dir_if_needed(self, tmp_path):
        new_dir = tmp_path / "new" / "results"
        path = write_result(new_dir, "test.py", {"exit_code": 0})
        assert path.exists()


class TestReadResult:
    def test_reads_written_result(self, results_dir):
        write_result(results_dir, "src/foo.py", {"exit_code": 0, "summary": "OK"})
        result = read_result(results_dir, "src/foo.py")
        assert result is not None
        assert result["exit_code"] == 0
        assert result["summary"] == "OK"

    def test_returns_none_for_missing(self, results_dir):
        result = read_result(results_dir, "nonexistent.py")
        assert result is None

    def test_returns_none_for_invalid_json(self, results_dir):
        (results_dir / "bad_json.json").write_text("not json{{{")
        result = read_result(results_dir, "bad.json")
        # sanitize_item_name("bad.json") = "bad_json"
        assert result is None


class TestCollectSummaries:
    def test_collects_from_results_dir(self, batch_dir):
        summaries = collect_summaries(batch_dir / "results")
        assert len(summaries) == 2
        items = [s["item"] for s in summaries]
        assert "src/bar.py" in items
        assert "src/foo.py" in items

    def test_summary_fields(self, batch_dir):
        summaries = collect_summaries(batch_dir / "results")
        for s in summaries:
            assert "item" in s
            assert "summary" in s
            assert "exit_code" in s

    def test_empty_dir(self, tmp_path):
        empty = tmp_path / "empty_results"
        empty.mkdir()
        summaries = collect_summaries(empty)
        assert summaries == []

    def test_nonexistent_dir(self, tmp_path):
        summaries = collect_summaries(tmp_path / "nonexistent")
        assert summaries == []


class TestGenerateReport:
    def test_produces_markdown(self, batch_dir):
        report = generate_report(batch_dir)
        assert "# Batch Report:" in report
        assert "test-batch" in report

    def test_has_summary_table(self, batch_dir):
        report = generate_report(batch_dir)
        assert "| Status | Count |" in report
        assert "| Total |" in report

    def test_lists_completed_items(self, batch_dir):
        report = generate_report(batch_dir)
        assert "## Completed Items" in report
        assert "src/foo.py" in report

    def test_lists_failed_items(self, batch_dir):
        report = generate_report(batch_dir)
        assert "## Failed Items" in report
        assert "src/bar.py" in report

    def test_lists_remaining_items(self, batch_dir):
        report = generate_report(batch_dir)
        assert "## Remaining Items" in report
        assert "src/baz.py" in report
