"""Tests for the batch orchestrator module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from claude_cli.batch.ledger import create_ledger
from claude_cli.batch.orchestrator import build_command, discover_items, find_claude_binary


@pytest.fixture
def project_dir(tmp_path):
    """Create a project with some Python files."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "auth.py").write_text("# auth")
    (src / "api.py").write_text("# api")
    (src / "models.py").write_text("# models")
    sub = src / "utils"
    sub.mkdir()
    (sub / "helpers.py").write_text("# helpers")
    return tmp_path


@pytest.fixture
def batch_dir(tmp_path):
    """Create a batch with a ledger."""
    bd = tmp_path / ".claude" / "batch" / "test-batch"
    items = ["src/auth.py", "src/api.py"]
    create_ledger("test-batch", items, "Review $item", {"pattern": "src/*.py", "parallel": 2}, bd)
    return bd


class TestDiscoverItems:
    def test_finds_python_files(self, project_dir):
        items = discover_items("src/*.py", project_dir)
        assert len(items) == 3
        assert "src/auth.py" in items

    def test_recursive_glob(self, project_dir):
        items = discover_items("src/**/*.py", project_dir)
        assert len(items) == 4
        assert "src/utils/helpers.py" in items

    def test_no_matches(self, project_dir):
        items = discover_items("*.rs", project_dir)
        assert items == []

    def test_sorted_output(self, project_dir):
        items = discover_items("src/*.py", project_dir)
        assert items == sorted(items)


class TestBuildCommand:
    def test_basic_command(self):
        cmd = build_command("src/auth.py", "Review $item for bugs")
        assert cmd[0] == "claude"
        assert cmd[1] == "-p"
        assert cmd[2] == "Review src/auth.py for bugs"
        assert "--output-format" in cmd
        assert "json" in cmd

    def test_with_allowed_tools(self):
        cmd = build_command("test.py", "Check $item", allowed_tools=["Read", "Grep"])
        assert "--allowedTools" in cmd
        idx = cmd.index("--allowedTools")
        assert cmd[idx + 1] == "Read,Grep"

    def test_max_turns(self):
        cmd = build_command("test.py", "Check $item", max_turns=30)
        assert "--max-turns" in cmd
        idx = cmd.index("--max-turns")
        assert cmd[idx + 1] == "30"

    def test_item_substitution(self):
        cmd = build_command("path/to/file.py", "Analyze $item thoroughly")
        assert "Analyze path/to/file.py thoroughly" in cmd

    def test_no_allowed_tools(self):
        cmd = build_command("test.py", "Check $item")
        assert "--allowedTools" not in cmd


class TestFindClaudeBinary:
    @patch("claude_cli.batch.orchestrator.shutil.which")
    def test_found(self, mock_which):
        mock_which.return_value = "/usr/local/bin/claude"
        assert find_claude_binary() == "/usr/local/bin/claude"

    @patch("claude_cli.batch.orchestrator.shutil.which")
    def test_not_found(self, mock_which):
        mock_which.return_value = None
        assert find_claude_binary() is None


class TestRunBatch:
    @patch("claude_cli.batch.orchestrator.subprocess.Popen")
    def test_spawns_processes(self, mock_popen, batch_dir):
        """Verify that run_batch spawns processes for pending items."""
        from claude_cli.batch.orchestrator import run_batch

        # Mock process that completes immediately
        mock_proc = MagicMock()
        mock_proc.poll.return_value = 0
        mock_proc.pid = 12345
        mock_popen.return_value = mock_proc

        summary = run_batch(batch_dir, parallel=2, poll_interval=0.01)

        # Should have spawned 2 processes (one per item)
        assert mock_popen.call_count == 2
        assert summary["done"] == 2
        assert summary["pending"] == 0

    @patch("claude_cli.batch.orchestrator.subprocess.Popen")
    def test_respects_parallel_limit(self, mock_popen, tmp_path):
        """Verify parallel limit is respected by checking spawn calls between polls."""
        from claude_cli.batch.orchestrator import run_batch

        # Create batch with 5 items but parallel=2
        bd = tmp_path / ".claude" / "batch" / "parallel-test"
        items = [f"file_{i}.py" for i in range(5)]
        create_ledger("parallel-test", items, "Check $item", {"parallel": 2}, bd)

        spawn_order = []

        def make_proc(*args, **kwargs):
            mock = MagicMock()
            mock.pid = 10000 + len(spawn_order)
            spawn_order.append(mock)
            # Each process completes on first poll
            mock.poll.return_value = 0
            return mock

        mock_popen.side_effect = make_proc
        summary = run_batch(bd, parallel=2, poll_interval=0.01)

        assert len(spawn_order) == 5  # All items processed
        assert summary["done"] == 5
        # The orchestrator spawns up to `parallel` before polling.
        # With instant completion, it cycles: spawn 2, poll (both done),
        # spawn 2, poll, spawn 1, poll. So it works correctly.

    @patch("claude_cli.batch.orchestrator.subprocess.Popen")
    def test_handles_failures(self, mock_popen, batch_dir):
        """Verify failed items are recorded correctly."""
        from claude_cli.batch.orchestrator import run_batch

        mock_proc = MagicMock()
        mock_proc.poll.return_value = 1  # Non-zero exit
        mock_proc.pid = 99999
        mock_popen.return_value = mock_proc

        summary = run_batch(batch_dir, parallel=2, poll_interval=0.01)
        assert summary["failed"] == 2
        assert summary["done"] == 0


class TestResumeBatch:
    @patch("claude_cli.batch.orchestrator.subprocess.Popen")
    def test_skips_completed(self, mock_popen, batch_dir):
        """Resume should only process pending/failed items."""
        from claude_cli.batch.ledger import update_item_status
        from claude_cli.batch.orchestrator import resume_batch

        # Mark first item as done
        ledger_path = batch_dir / "ledger.yaml"
        update_item_status(ledger_path, "src/auth.py", "done", exit_code=0)

        mock_proc = MagicMock()
        mock_proc.poll.return_value = 0
        mock_proc.pid = 11111
        mock_popen.return_value = mock_proc

        summary = resume_batch(batch_dir, parallel=2)

        # Should only spawn 1 process (the pending item)
        assert mock_popen.call_count == 1
