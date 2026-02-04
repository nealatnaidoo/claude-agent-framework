"""Tests for worktree module."""

import pytest

from claude_cli.worktree.cli import _parse_worktree_list


class TestWorktreeParser:
    def test_parse_empty(self):
        """Test parsing empty output."""
        result = _parse_worktree_list("")
        assert result == []

    def test_parse_single_worktree(self):
        """Test parsing single worktree."""
        output = """worktree /path/to/repo
HEAD abc123def456
branch refs/heads/main
"""
        result = _parse_worktree_list(output)
        assert len(result) == 1
        assert result[0]["path"] == "/path/to/repo"
        assert result[0]["commit"] == "abc123def456"
        assert result[0]["branch"] == "main"

    def test_parse_multiple_worktrees(self):
        """Test parsing multiple worktrees."""
        output = """worktree /path/to/main
HEAD abc123
branch refs/heads/main

worktree /path/to/feature
HEAD def456
branch refs/heads/feature/auth
"""
        result = _parse_worktree_list(output)
        assert len(result) == 2
        assert result[0]["branch"] == "main"
        assert result[1]["branch"] == "feature/auth"

    def test_parse_detached_head(self):
        """Test parsing detached HEAD state."""
        output = """worktree /path/to/repo
HEAD abc123
detached
"""
        result = _parse_worktree_list(output)
        assert len(result) == 1
        assert result[0]["branch"] == "(detached)"

    def test_parse_branch_without_refs_heads(self):
        """Test that refs/heads/ prefix is stripped."""
        output = """worktree /path/to/repo
HEAD abc123
branch refs/heads/feature/user-auth
"""
        result = _parse_worktree_list(output)
        assert result[0]["branch"] == "feature/user-auth"
