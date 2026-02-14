"""Tests for the batch ledger module."""

import os
from pathlib import Path

import pytest
import yaml

from claude_cli.batch.ledger import (
    _sanitize_name,
    create_ledger,
    generate_batch_id,
    get_active_items,
    get_ledger_summary,
    get_resumable_items,
    load_ledger,
    reset_stale_active,
    update_item_status,
)


@pytest.fixture
def batch_dir(tmp_path):
    """Create a temporary batch directory."""
    bd = tmp_path / ".claude" / "batch" / "test-batch"
    return bd


@pytest.fixture
def sample_items():
    return ["src/auth/service.py", "src/api/routes.py", "src/db/models.py"]


@pytest.fixture
def ledger_path(batch_dir, sample_items):
    """Create a ledger and return its path."""
    return create_ledger(
        batch_id="test-batch",
        items=sample_items,
        prompt_template="Review $item for issues",
        config={"pattern": "src/**/*.py", "parallel": 3, "max_turns": 20},
        batch_dir=batch_dir,
    )


class TestGenerateBatchId:
    def test_generates_unique_id(self):
        bid = generate_batch_id()
        assert bid.startswith("batch-")
        assert len(bid) > 15  # batch-YYYYMMDD-HHMMSS

    def test_format(self):
        bid = generate_batch_id()
        parts = bid.split("-")
        assert parts[0] == "batch"
        assert len(parts[1]) == 8  # date
        assert len(parts[2]) == 6  # time


class TestCreateLedger:
    def test_creates_ledger_file(self, ledger_path, batch_dir):
        assert ledger_path.exists()
        assert ledger_path.name == "ledger.yaml"
        assert ledger_path.parent == batch_dir

    def test_creates_results_dir(self, ledger_path, batch_dir):
        assert (batch_dir / "results").is_dir()

    def test_ledger_schema(self, ledger_path, sample_items):
        data = yaml.safe_load(ledger_path.read_text())
        assert data["schema_version"] == "1.0"
        assert data["batch_id"] == "test-batch"
        assert data["created_at"] is not None
        assert data["updated_at"] is not None

    def test_all_items_pending(self, ledger_path, sample_items):
        data = yaml.safe_load(ledger_path.read_text())
        assert len(data["items"]) == len(sample_items)
        for item in data["items"]:
            assert item["status"] == "pending"
            assert item["started_at"] is None
            assert item["completed_at"] is None
            assert item["pid"] is None

    def test_summary_counts(self, ledger_path, sample_items):
        data = yaml.safe_load(ledger_path.read_text())
        assert data["summary"]["total"] == 3
        assert data["summary"]["pending"] == 3
        assert data["summary"]["active"] == 0
        assert data["summary"]["done"] == 0
        assert data["summary"]["failed"] == 0

    def test_config_stored(self, ledger_path):
        data = yaml.safe_load(ledger_path.read_text())
        assert data["config"]["prompt_template"] == "Review $item for issues"
        assert data["config"]["pattern"] == "src/**/*.py"
        assert data["config"]["parallel"] == 3

    def test_result_file_paths(self, ledger_path):
        data = yaml.safe_load(ledger_path.read_text())
        item = data["items"][0]
        assert item["result_file"] == "results/src_auth_service_py.json"


class TestLoadLedger:
    def test_roundtrip(self, ledger_path, sample_items):
        data = load_ledger(ledger_path)
        assert data["batch_id"] == "test-batch"
        assert len(data["items"]) == len(sample_items)

    def test_raises_on_missing(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_ledger(tmp_path / "nonexistent.yaml")


class TestUpdateItemStatus:
    def test_pending_to_active(self, ledger_path):
        update_item_status(ledger_path, "src/auth/service.py", "active", pid=12345)
        data = load_ledger(ledger_path)
        item = data["items"][0]
        assert item["status"] == "active"
        assert item["started_at"] is not None
        assert item["pid"] == 12345

    def test_active_to_done(self, ledger_path):
        update_item_status(ledger_path, "src/auth/service.py", "active", pid=100)
        update_item_status(
            ledger_path,
            "src/auth/service.py",
            "done",
            result_summary="All clear",
            exit_code=0,
        )
        data = load_ledger(ledger_path)
        item = data["items"][0]
        assert item["status"] == "done"
        assert item["completed_at"] is not None
        assert item["summary"] == "All clear"
        assert item["exit_code"] == 0

    def test_active_to_failed(self, ledger_path):
        update_item_status(ledger_path, "src/api/routes.py", "active", pid=200)
        update_item_status(
            ledger_path,
            "src/api/routes.py",
            "failed",
            result_summary="Timeout",
            exit_code=1,
        )
        data = load_ledger(ledger_path)
        item = data["items"][1]
        assert item["status"] == "failed"
        assert item["exit_code"] == 1

    def test_summary_recomputed(self, ledger_path):
        update_item_status(ledger_path, "src/auth/service.py", "done", exit_code=0)
        update_item_status(ledger_path, "src/api/routes.py", "failed", exit_code=1)
        data = load_ledger(ledger_path)
        assert data["summary"]["done"] == 1
        assert data["summary"]["failed"] == 1
        assert data["summary"]["pending"] == 1

    def test_updated_at_changes(self, ledger_path):
        before = load_ledger(ledger_path)["updated_at"]
        update_item_status(ledger_path, "src/auth/service.py", "active", pid=1)
        after = load_ledger(ledger_path)["updated_at"]
        assert after >= before


class TestGetResumableItems:
    def test_all_pending(self, ledger_path, sample_items):
        items = get_resumable_items(ledger_path)
        assert len(items) == 3

    def test_excludes_done(self, ledger_path):
        update_item_status(ledger_path, "src/auth/service.py", "done", exit_code=0)
        items = get_resumable_items(ledger_path)
        assert "src/auth/service.py" not in items
        assert len(items) == 2

    def test_includes_failed(self, ledger_path):
        update_item_status(ledger_path, "src/auth/service.py", "failed", exit_code=1)
        items = get_resumable_items(ledger_path)
        assert "src/auth/service.py" in items

    def test_excludes_active(self, ledger_path):
        update_item_status(ledger_path, "src/auth/service.py", "active", pid=1)
        items = get_resumable_items(ledger_path)
        assert "src/auth/service.py" not in items


class TestGetActiveItems:
    def test_returns_active(self, ledger_path):
        update_item_status(ledger_path, "src/auth/service.py", "active", pid=100)
        active = get_active_items(ledger_path)
        assert len(active) == 1
        assert active[0]["name"] == "src/auth/service.py"

    def test_empty_when_none_active(self, ledger_path):
        active = get_active_items(ledger_path)
        assert len(active) == 0


class TestGetLedgerSummary:
    def test_initial_summary(self, ledger_path):
        summary = get_ledger_summary(ledger_path)
        assert summary["total"] == 3
        assert summary["pending"] == 3

    def test_after_updates(self, ledger_path):
        update_item_status(ledger_path, "src/auth/service.py", "done", exit_code=0)
        update_item_status(ledger_path, "src/api/routes.py", "active", pid=1)
        summary = get_ledger_summary(ledger_path)
        assert summary["done"] == 1
        assert summary["active"] == 1
        assert summary["pending"] == 1


class TestResetStaleActive:
    def test_resets_dead_process(self, ledger_path):
        # Use a PID that almost certainly doesn't exist
        update_item_status(ledger_path, "src/auth/service.py", "active", pid=999999999)
        reset = reset_stale_active(ledger_path)
        assert "src/auth/service.py" in reset
        data = load_ledger(ledger_path)
        assert data["items"][0]["status"] == "pending"

    def test_no_reset_when_no_active(self, ledger_path):
        reset = reset_stale_active(ledger_path)
        assert reset == []


class TestSanitizeName:
    def test_basic_path(self):
        assert _sanitize_name("src/auth/service.py") == "src_auth_service_py"

    def test_no_slashes(self):
        assert _sanitize_name("file.py") == "file_py"

    def test_deep_path(self):
        assert _sanitize_name("a/b/c/d.txt") == "a_b_c_d_txt"

    def test_windows_path(self):
        assert _sanitize_name("src\\auth\\service.py") == "src_auth_service_py"
