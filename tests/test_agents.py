"""Tests for agents module."""

import pytest
from pathlib import Path

from claude_cli.agents.validator import AgentValidator, ValidationResult


class TestAgentValidator:
    def test_validate_valid_agent(self, temp_agents_dir):
        """Test validation of a valid agent."""
        validator = AgentValidator()
        agent_file = temp_agents_dir / "test-agent.md"
        results = validator.validate_file(agent_file)

        # Check that some validations passed
        passed = [r for r in results if r.passed]
        assert len(passed) > 0

    def test_validate_missing_file(self, tmp_path):
        """Test validation of non-existent file."""
        validator = AgentValidator()
        results = validator.validate_file(tmp_path / "nonexistent.md")

        assert len(results) == 1
        assert not results[0].passed
        assert "not found" in results[0].message.lower()

    def test_validate_missing_frontmatter(self, tmp_path):
        """Test validation of agent without frontmatter."""
        agent_file = tmp_path / "no-frontmatter.md"
        agent_file.write_text("# Agent\n\nNo frontmatter here.")

        validator = AgentValidator()
        results = validator.validate_file(agent_file)

        errors = [r for r in results if not r.passed and r.severity == "error"]
        frontmatter_error = [r for r in errors if "frontmatter" in r.name]
        assert len(frontmatter_error) > 0

    def test_validate_all_agents(self, temp_agents_dir):
        """Test validation of all agents in directory."""
        validator = AgentValidator()
        results = validator.validate_all_agents(temp_agents_dir)

        assert "test-agent.md" in results
        assert len(results["test-agent.md"]) > 0


class TestValidationResult:
    def test_validation_result_creation(self):
        """Test ValidationResult dataclass."""
        result = ValidationResult(
            name="test_check",
            passed=True,
            severity="error",
            message="Test passed",
        )

        assert result.name == "test_check"
        assert result.passed is True
        assert result.severity == "error"
        assert result.message == "Test passed"
