"""Tests for portfolio cockpit generator."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from claude_cli.cockpit.portfolio import (
    collect_portfolio_data,
    discover_projects,
    generate_portfolio_cockpit,
    render_portfolio_html,
)

# All tests patch out the real registry so local machine state doesn't leak in
@pytest.fixture(autouse=True)
def _isolate_from_registry(tmp_path, monkeypatch):
    """Prevent tests from reading the real ~/.claude/devops/project_registry.yaml."""
    fake_home = tmp_path / "fake_home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    # Also patch Path.home() which may be cached
    monkeypatch.setattr(Path, "home", staticmethod(lambda: fake_home))
    yield


def _make_project(base: Path, name: str, phase: str = "coding", tasks: int = 3) -> Path:
    """Helper: create a minimal governed project."""
    project = base / name
    claude_dir = project / ".claude"
    claude_dir.mkdir(parents=True)

    task_items = ""
    for i in range(tasks):
        status = ["completed", "in_progress", "pending"][i % 3]
        task_items += (
            f'    - id: "T{i+1:03d}"\n'
            f'      title: "Task {i+1}"\n'
            f'      status: "{status}"\n'
        )

    (claude_dir / "manifest.yaml").write_text(
        f'schema_version: "1.4"\n'
        f'project_slug: "{name}"\n'
        f'project_name: "{name.replace("-", " ").title()}"\n'
        f'phase: "{phase}"\n'
        f'last_updated: "2026-02-14T12:00:00Z"\n'
        f"outstanding:\n  tasks:\n{task_items}"
    )
    return project


@pytest.fixture
def portfolio_dir(tmp_path):
    """Create a base directory with multiple governed projects."""
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    _make_project(projects_dir, "alpha-app", phase="coding", tasks=6)
    _make_project(projects_dir, "beta-service", phase="qa", tasks=3)
    _make_project(projects_dir, "gamma-lib", phase="complete", tasks=9)
    return tmp_path


class TestDiscoverProjects:
    def test_discovers_via_glob(self, portfolio_dir):
        projects = discover_projects(portfolio_dir)
        slugs = {p.name for p in projects}
        assert "alpha-app" in slugs
        assert "beta-service" in slugs
        assert "gamma-lib" in slugs

    def test_deduplicates(self, portfolio_dir):
        # Also add a top-level project that duplicates one in projects/
        top_level = portfolio_dir / "alpha-app"
        top_level.mkdir(exist_ok=True)
        (top_level / ".claude").mkdir(exist_ok=True)
        (top_level / ".claude" / "manifest.yaml").write_text("phase: coding\n")

        projects = discover_projects(portfolio_dir)
        # Should have unique projects (3 under projects/ + 1 top-level)
        resolved = {p.resolve() for p in projects}
        assert len(resolved) == len(projects)

    def test_discovers_from_registry(self, portfolio_dir, tmp_path):
        # Create a registry pointing to an extra project
        _make_project(tmp_path, "extra-project", phase="ba")
        extra = tmp_path / "extra-project"

        # Write registry to the fake home used by _isolate_from_registry
        fake_home = Path.home()  # patched by autouse fixture
        registry_dir = fake_home / ".claude" / "devops"
        registry_dir.mkdir(parents=True, exist_ok=True)
        (registry_dir / "project_registry.yaml").write_text(
            f"projects:\n  - {extra}\n"
        )

        projects = discover_projects(portfolio_dir)
        slugs = {p.name for p in projects}
        assert "extra-project" in slugs

    def test_empty_base_dir(self, tmp_path):
        projects = discover_projects(tmp_path)
        assert projects == []


class TestCollectPortfolioData:
    def test_aggregation_counts(self, portfolio_dir):
        projects = discover_projects(portfolio_dir)
        data = collect_portfolio_data(projects)

        assert data["project_count"] == 3
        assert len(data["projects"]) == 3

        # Each project has tasks in round-robin: completed, in_progress, pending
        # alpha: 6 tasks -> 2 completed, 2 in_progress, 2 pending
        # beta: 3 tasks -> 1 completed, 1 in_progress, 1 pending
        # gamma: 9 tasks -> 3 completed, 3 in_progress, 3 pending
        assert data["totals"]["tasks_completed"] == 6
        assert data["totals"]["tasks_in_progress"] == 6
        assert data["totals"]["tasks_pending"] == 6

    def test_phase_distribution(self, portfolio_dir):
        projects = discover_projects(portfolio_dir)
        data = collect_portfolio_data(projects)
        assert data["phase_distribution"]["coding"] == 1
        assert data["phase_distribution"]["qa"] == 1
        assert data["phase_distribution"]["complete"] == 1

    def test_project_summaries(self, portfolio_dir):
        projects = discover_projects(portfolio_dir)
        data = collect_portfolio_data(projects)
        slugs = {p["slug"] for p in data["projects"]}
        assert "alpha-app" in slugs

    def test_empty_portfolio(self, tmp_path):
        data = collect_portfolio_data([])
        assert data["project_count"] == 0
        assert data["projects"] == []
        assert data["totals"]["tasks_completed"] == 0


class TestRenderPortfolioHtml:
    def test_produces_valid_html(self, portfolio_dir):
        projects = discover_projects(portfolio_dir)
        data = collect_portfolio_data(projects)
        html = render_portfolio_html(data)
        assert "<!DOCTYPE html>" in html
        assert "Portfolio Cockpit" in html

    def test_contains_expected_sections(self, portfolio_dir):
        projects = discover_projects(portfolio_dir)
        data = collect_portfolio_data(projects)
        html = render_portfolio_html(data)
        assert "Phase Distribution" in html
        assert "Projects" in html
        assert "PHASE_COLORS" in html

    def test_embeds_data_as_json(self, portfolio_dir):
        projects = discover_projects(portfolio_dir)
        data = collect_portfolio_data(projects)
        html = render_portfolio_html(data)
        start = html.index("DATA = ") + len("DATA = ")
        end = html.index(";\n", start)
        embedded = json.loads(html[start:end])
        assert embedded["project_count"] == 3

    def test_uses_dark_theme(self, portfolio_dir):
        projects = discover_projects(portfolio_dir)
        data = collect_portfolio_data(projects)
        html = render_portfolio_html(data)
        assert "#0f172a" in html
        assert "#1e293b" in html

    def test_empty_portfolio_renders(self):
        data = collect_portfolio_data([])
        html = render_portfolio_html(data)
        assert "<!DOCTYPE html>" in html
        assert "No governed projects found" in html or "0 projects" in html


class TestGeneratePortfolioCockpit:
    def test_writes_html_file(self, portfolio_dir, tmp_path):
        output = tmp_path / "portfolio.html"
        result = generate_portfolio_cockpit(portfolio_dir, output=output)
        assert result == output
        assert output.exists()
        assert "<!DOCTYPE html>" in output.read_text()

    def test_single_project(self, tmp_path):
        _make_project(tmp_path / "projects", "solo-app", phase="coding", tasks=2)
        output = tmp_path / "out.html"
        result = generate_portfolio_cockpit(tmp_path, output=output)
        assert result.exists()
        content = result.read_text()
        assert "Solo App" in content or "solo-app" in content.lower()
