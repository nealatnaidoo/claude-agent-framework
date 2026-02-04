"""Tests for versioning module."""

import pytest
import json
from datetime import datetime, timezone
from pathlib import Path

from claude_cli.versioning.tracker import (
    load_history,
    save_history,
    scan_changes,
    apply_changes,
    get_state_at,
    compute_checksum,
)


class TestChecksum:
    def test_compute_checksum(self, tmp_path):
        """Test checksum computation."""
        file = tmp_path / "test.txt"
        file.write_text("Hello, World!")

        checksum = compute_checksum(file)
        assert len(checksum) == 16  # Truncated SHA256

    def test_checksum_consistency(self, tmp_path):
        """Test that same content gives same checksum."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("Same content")
        file2.write_text("Same content")

        assert compute_checksum(file1) == compute_checksum(file2)

    def test_checksum_different_content(self, tmp_path):
        """Test that different content gives different checksum."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("Content A")
        file2.write_text("Content B")

        assert compute_checksum(file1) != compute_checksum(file2)


class TestHistoryOperations:
    def test_load_empty_history(self, tmp_path, monkeypatch):
        """Test loading non-existent history."""
        monkeypatch.setattr(
            "claude_cli.versioning.tracker.get_history_file",
            lambda: tmp_path / "nonexistent" / "history.json"
        )
        history = load_history()
        assert history["schema_version"] == "1.0"
        assert history["records"] == []
        assert history["snapshots"] == []

    def test_save_and_load_history(self, tmp_path, monkeypatch):
        """Test saving and loading history."""
        history_file = tmp_path / "history.json"
        monkeypatch.setattr(
            "claude_cli.versioning.tracker.get_history_file",
            lambda: history_file
        )

        history = {
            "schema_version": "1.0",
            "records": [{"test": "record"}],
            "snapshots": []
        }
        save_history(history)

        loaded = load_history()
        assert loaded["records"] == [{"test": "record"}]


class TestApplyChanges:
    def test_apply_new_record(self):
        """Test applying a new record."""
        history = {"schema_version": "1.0", "records": [], "snapshots": []}
        changes = [{
            "file_path": "test.md",
            "component_type": "test",
            "component_name": "test",
            "checksum": "abc123",
            "version": "1.0.0",
            "valid_from": "2026-01-01",
            "valid_to": None,
            "recorded_at": "2026-01-01",
            "change_type": "initial",
            "change_summary": "Initial",
        }]

        applied = apply_changes(history, changes)
        assert applied == 1
        assert len(history["records"]) == 1
        assert history["records"][0]["file_path"] == "test.md"

    def test_apply_close_record(self):
        """Test closing an existing record."""
        history = {
            "schema_version": "1.0",
            "records": [{
                "file_path": "test.md",
                "valid_from": "2026-01-01",
                "valid_to": None,
            }],
            "snapshots": []
        }
        changes = [{
            "action": "close",
            "file_path": "test.md",
            "valid_to": "2026-02-01",
        }]

        apply_changes(history, changes)
        assert history["records"][0]["valid_to"] == "2026-02-01"


class TestGetStateAt:
    def test_get_state_at_current(self):
        """Test getting current state."""
        now = datetime.now(timezone.utc)
        history = {
            "schema_version": "1.0",
            "records": [{
                "file_path": "test.md",
                "component_type": "test",
                "component_name": "test",
                "valid_from": "2026-01-01T00:00:00+00:00",
                "valid_to": None,
            }],
            "snapshots": []
        }

        state = get_state_at(history, now)
        assert len(state) == 1
        assert state[0]["file_path"] == "test.md"

    def test_get_state_at_past(self):
        """Test getting state before record was created."""
        history = {
            "schema_version": "1.0",
            "records": [{
                "file_path": "test.md",
                "component_type": "test",
                "component_name": "test",
                "valid_from": "2026-02-01T00:00:00+00:00",
                "valid_to": None,
            }],
            "snapshots": []
        }

        past = datetime(2026, 1, 1, tzinfo=timezone.utc)
        state = get_state_at(history, past)
        assert len(state) == 0

    def test_get_state_at_with_closed_record(self):
        """Test that closed records are not included after close date."""
        history = {
            "schema_version": "1.0",
            "records": [{
                "file_path": "test.md",
                "component_type": "test",
                "component_name": "test",
                "valid_from": "2026-01-01T00:00:00+00:00",
                "valid_to": "2026-02-01T00:00:00+00:00",
            }],
            "snapshots": []
        }

        # During valid period
        during = datetime(2026, 1, 15, tzinfo=timezone.utc)
        state = get_state_at(history, during)
        assert len(state) == 1

        # After valid period
        after = datetime(2026, 3, 1, tzinfo=timezone.utc)
        state = get_state_at(history, after)
        assert len(state) == 0
