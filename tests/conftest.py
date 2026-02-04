"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path
from typer.testing import CliRunner


@pytest.fixture
def cli_runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_agents_dir(tmp_path):
    """Create a temporary agents directory with sample agents."""
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()

    # Create a sample agent
    sample_agent = agents_dir / "test-agent.md"
    sample_agent.write_text("""---
name: test-agent
description: A test agent
tools: [Read, Glob]
model: sonnet
---

# test-agent

## Identity

This is an **INTERNAL agent** that participates in the core development workflow.

## Entry Protocol

On activation, read `.claude/manifest.yaml` first.

## Manifest Update

Update manifest after completing work.
""")

    return agents_dir


@pytest.fixture
def sample_graph():
    """Create a sample dependency graph."""
    return {
        "agent-a": {
            "name": "agent-a",
            "scope": "micro",
            "depends_on": [],
            "depended_by": ["agent-b"],
        },
        "agent-b": {
            "name": "agent-b",
            "scope": "micro",
            "depends_on": ["agent-a"],
            "depended_by": ["agent-c"],
        },
        "agent-c": {
            "name": "agent-c",
            "scope": "micro",
            "depends_on": ["agent-b"],
            "depended_by": [],
        },
    }
