"""Tests for analysis module."""

import pytest

from claude_cli.analysis.graph import get_all_dependencies, get_all_dependents
from claude_cli.analysis.impact import (
    analyze_modification_impact,
    analyze_deletion_impact,
    analyze_add_dependency,
)


class TestDependencyGraph:
    def test_get_all_dependencies(self, sample_graph):
        """Test transitive dependency resolution."""
        deps = get_all_dependencies(sample_graph, "agent-c")
        assert "agent-b" in deps
        assert "agent-a" in deps

    def test_get_all_dependencies_no_deps(self, sample_graph):
        """Test agent with no dependencies."""
        deps = get_all_dependencies(sample_graph, "agent-a")
        assert len(deps) == 0

    def test_get_all_dependents(self, sample_graph):
        """Test transitive dependents resolution."""
        dependents = get_all_dependents(sample_graph, "agent-a")
        assert "agent-b" in dependents
        assert "agent-c" in dependents

    def test_get_all_dependents_no_dependents(self, sample_graph):
        """Test agent with no dependents."""
        dependents = get_all_dependents(sample_graph, "agent-c")
        assert len(dependents) == 0


class TestImpactAnalysis:
    def test_modification_impact(self, sample_graph):
        """Test modification impact analysis."""
        impact = analyze_modification_impact(sample_graph, "agent-a")
        assert impact["agent"] == "agent-a"
        assert impact["action"] == "modify"
        assert "agent-b" in impact["direct_dependents"]

    def test_deletion_impact_blocked(self, sample_graph):
        """Test deletion impact when blocked by dependents."""
        impact = analyze_deletion_impact(sample_graph, "agent-a")
        assert impact["can_delete"] is False
        assert len(impact["blocking_dependents"]) > 0

    def test_deletion_impact_allowed(self, sample_graph):
        """Test deletion impact when no dependents."""
        impact = analyze_deletion_impact(sample_graph, "agent-c")
        assert impact["can_delete"] is True
        assert len(impact["blocking_dependents"]) == 0

    def test_add_dependency_circular(self, sample_graph):
        """Test circular dependency detection."""
        impact = analyze_add_dependency(sample_graph, "agent-a", "agent-c")
        assert "error" in impact
        assert "CIRCULAR" in impact["error"]

    def test_add_dependency_valid(self, sample_graph):
        """Test valid dependency addition."""
        # Add a new agent that doesn't create a cycle
        sample_graph["agent-d"] = {
            "name": "agent-d",
            "scope": "micro",
            "depends_on": [],
            "depended_by": [],
        }
        impact = analyze_add_dependency(sample_graph, "agent-c", "agent-d")
        assert "error" not in impact
        assert impact["new_dependency"] == "agent-d"

    def test_agent_not_found(self, sample_graph):
        """Test error when agent not found."""
        impact = analyze_modification_impact(sample_graph, "nonexistent")
        assert "error" in impact
