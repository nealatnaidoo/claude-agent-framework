"""Tests for db harness module."""

import pytest
import json

from claude_cli.db.drift import DriftReport


class TestDriftReport:
    def test_empty_report(self):
        """Test empty drift report."""
        report = DriftReport()
        assert report.missing_tables == []
        assert report.missing_columns == {}
        assert report.type_mismatches == []
        assert not report.has_breaking_changes

    def test_breaking_changes_missing_tables(self):
        """Test that missing tables are breaking changes."""
        report = DriftReport(missing_tables=["users", "orders"])
        assert report.has_breaking_changes

    def test_breaking_changes_type_mismatches(self):
        """Test that type mismatches are breaking changes."""
        report = DriftReport(
            type_mismatches=[
                {"table": "users", "column": "id", "source": "int", "target": "varchar"}
            ]
        )
        assert report.has_breaking_changes

    def test_non_breaking_changes(self):
        """Test that missing columns alone are not breaking."""
        report = DriftReport(
            missing_columns={"users": ["middle_name", "nickname"]}
        )
        assert not report.has_breaking_changes

    def test_to_json(self):
        """Test JSON export."""
        report = DriftReport(
            missing_tables=["orders"],
            missing_columns={"users": ["phone"]},
        )
        json_str = report.to_json()
        data = json.loads(json_str)

        assert data["missing_tables"] == ["orders"]
        assert data["missing_columns"] == {"users": ["phone"]}
        assert data["has_breaking_changes"] is True

    def test_json_roundtrip(self):
        """Test that JSON can be parsed back."""
        report = DriftReport(
            missing_tables=["t1"],
            type_mismatches=[{"table": "t2", "column": "c1", "source": "int", "target": "text"}],
        )
        json_str = report.to_json()
        data = json.loads(json_str)

        # Verify structure
        assert "missing_tables" in data
        assert "missing_columns" in data
        assert "type_mismatches" in data
        assert "index_differences" in data
        assert "has_breaking_changes" in data
