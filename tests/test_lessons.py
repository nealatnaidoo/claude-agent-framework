"""Tests for lessons module."""

import pytest
from datetime import date
from pathlib import Path

from claude_cli.lessons.models import Lesson, LessonCreate
from claude_cli.lessons.db import LessonsDB


class TestLessonModels:
    def test_lesson_create(self):
        """Test LessonCreate model."""
        lesson = LessonCreate(
            title="Test Lesson",
            problem="Something broke",
            solution="Fixed it",
            tags=["testing", "python"],
        )
        assert lesson.title == "Test Lesson"
        assert lesson.severity == "medium"  # default
        assert "testing" in lesson.tags

    def test_lesson_model(self):
        """Test Lesson model."""
        lesson = Lesson(
            id=1,
            number=124,
            title="Test Lesson",
            date_learned=date.today(),
            problem="Problem text",
            solution="Solution text",
            tags=["test"],
        )
        assert lesson.number == 124
        assert lesson.severity == "medium"

    def test_lesson_defaults(self):
        """Test Lesson default values."""
        lesson = Lesson(
            title="Minimal",
            problem="Problem",
            solution="Solution",
        )
        assert lesson.id == 0
        assert lesson.number is None
        assert lesson.tags == []
        assert lesson.checklist == []


class TestLessonsDB:
    @pytest.fixture
    def db(self, tmp_path):
        """Create a test database."""
        db_path = tmp_path / "test_lessons.duckdb"
        return LessonsDB(db_path)

    def test_add_lesson(self, db):
        """Test adding a lesson."""
        lesson_input = LessonCreate(
            title="Test Lesson",
            problem="Test problem",
            solution="Test solution",
            tags=["test"],
        )
        lesson = db.add(lesson_input)
        assert lesson.number == 1
        assert lesson.title == "Test Lesson"

    def test_get_lesson(self, db):
        """Test getting a lesson by number."""
        lesson_input = LessonCreate(
            title="Test Lesson",
            problem="Test problem",
            solution="Test solution",
        )
        db.add(lesson_input)
        lesson = db.get(1)
        assert lesson is not None
        assert lesson.title == "Test Lesson"

    def test_get_nonexistent(self, db):
        """Test getting a nonexistent lesson."""
        lesson = db.get(999)
        assert lesson is None

    def test_count(self, db):
        """Test lesson count."""
        assert db.count() == 0

        db.add(LessonCreate(title="L1", problem="P", solution="S"))
        assert db.count() == 1

        db.add(LessonCreate(title="L2", problem="P", solution="S"))
        assert db.count() == 2

    def test_list_all(self, db):
        """Test listing all lessons."""
        db.add(LessonCreate(title="L1", problem="P", solution="S"))
        db.add(LessonCreate(title="L2", problem="P", solution="S"))

        lessons = db.list_all()
        assert len(lessons) == 2
        # Should be in descending order by number
        assert lessons[0].number == 2
        assert lessons[1].number == 1

    def test_search_by_query(self, db):
        """Test searching by text query."""
        db.add(LessonCreate(title="Python Testing", problem="P", solution="S"))
        db.add(LessonCreate(title="JavaScript Debugging", problem="P", solution="S"))

        results = db.search(query="Python")
        assert len(results) == 1
        assert results[0].title == "Python Testing"

    def test_search_by_severity(self, db):
        """Test searching by severity."""
        db.add(LessonCreate(title="L1", problem="P", solution="S", severity="high"))
        db.add(LessonCreate(title="L2", problem="P", solution="S", severity="low"))

        results = db.search(severity="high")
        assert len(results) == 1
        assert results[0].severity == "high"

    def test_get_tags(self, db):
        """Test getting unique tags."""
        db.add(LessonCreate(title="L1", problem="P", solution="S", tags=["python", "testing"]))
        db.add(LessonCreate(title="L2", problem="P", solution="S", tags=["python", "api"]))

        tags = db.get_tags()
        assert "python" in tags
        assert "testing" in tags
        assert "api" in tags
        assert len(tags) == 3

    def test_export_markdown(self, db):
        """Test markdown export."""
        db.add(LessonCreate(
            title="Test Export",
            problem="Test problem",
            solution="Test solution",
        ))

        markdown = db.export_markdown()
        assert "# Development Lessons" in markdown
        assert "## Lesson 1: Test Export" in markdown
        assert "Test problem" in markdown
        assert "Test solution" in markdown

    def test_auto_increment_number(self, db):
        """Test that lesson numbers auto-increment."""
        lesson1 = db.add(LessonCreate(title="L1", problem="P", solution="S"))
        lesson2 = db.add(LessonCreate(title="L2", problem="P", solution="S"))
        lesson3 = db.add(LessonCreate(title="L3", problem="P", solution="S"))

        assert lesson1.number == 1
        assert lesson2.number == 2
        assert lesson3.number == 3
