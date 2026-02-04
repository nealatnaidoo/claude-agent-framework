"""DuckDB operations for lessons."""

from datetime import date
from pathlib import Path
from typing import Optional

import duckdb

from claude_cli.common.config import get_db_path
from claude_cli.lessons.models import Lesson, LessonCreate


SCHEMA_SQL = """
CREATE SEQUENCE IF NOT EXISTS seq_lessons_id START 1;

CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_lessons_id'),
    number INTEGER UNIQUE,
    title VARCHAR NOT NULL,
    date_learned DATE NOT NULL,
    project VARCHAR,
    context VARCHAR,
    problem TEXT NOT NULL,
    solution TEXT NOT NULL,
    tags VARCHAR[],
    checklist VARCHAR[],
    severity VARCHAR DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_lessons_date ON lessons(date_learned);
CREATE INDEX IF NOT EXISTS idx_lessons_project ON lessons(project);
CREATE INDEX IF NOT EXISTS idx_lessons_severity ON lessons(severity);
"""


class LessonsDB:
    """Database operations for lessons."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or get_db_path("lessons.duckdb")
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        """Ensure database schema exists."""
        with duckdb.connect(str(self.db_path)) as conn:
            conn.execute(SCHEMA_SQL)

    def _get_next_number(self, conn: duckdb.DuckDBPyConnection) -> int:
        """Get next lesson number."""
        result = conn.execute("SELECT MAX(number) FROM lessons").fetchone()
        return (result[0] or 0) + 1

    def add(self, lesson: LessonCreate) -> Lesson:
        """Add a new lesson."""
        with duckdb.connect(str(self.db_path)) as conn:
            next_num = self._get_next_number(conn)

            conn.execute(
                """
                INSERT INTO lessons (number, title, date_learned, project, context,
                                    problem, solution, tags, checklist, severity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    next_num,
                    lesson.title,
                    date.today(),
                    lesson.project,
                    lesson.context,
                    lesson.problem,
                    lesson.solution,
                    lesson.tags,
                    lesson.checklist,
                    lesson.severity,
                ],
            )

            result = conn.execute(
                "SELECT * FROM lessons WHERE number = ?", [next_num]
            ).fetchone()

            return self._row_to_lesson(result)

    def get(self, number: int) -> Optional[Lesson]:
        """Get a lesson by number."""
        with duckdb.connect(str(self.db_path)) as conn:
            result = conn.execute(
                "SELECT * FROM lessons WHERE number = ?", [number]
            ).fetchone()
            return self._row_to_lesson(result) if result else None

    def search(
        self,
        query: Optional[str] = None,
        tags: Optional[list[str]] = None,
        project: Optional[str] = None,
        severity: Optional[str] = None,
        since: Optional[date] = None,
        limit: int = 50,
    ) -> list[Lesson]:
        """Search lessons with filters."""
        conditions = []
        params: list = []

        if query:
            conditions.append(
                "(title ILIKE ? OR problem ILIKE ? OR solution ILIKE ?)"
            )
            pattern = f"%{query}%"
            params.extend([pattern, pattern, pattern])

        if tags:
            conditions.append("tags && ?")
            params.append(tags)

        if project:
            conditions.append("project ILIKE ?")
            params.append(f"%{project}%")

        if severity:
            conditions.append("severity = ?")
            params.append(severity)

        if since:
            conditions.append("date_learned >= ?")
            params.append(since)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        with duckdb.connect(str(self.db_path)) as conn:
            results = conn.execute(
                f"""
                SELECT * FROM lessons
                WHERE {where_clause}
                ORDER BY number DESC
                LIMIT ?
                """,
                [*params, limit],
            ).fetchall()

            return [self._row_to_lesson(row) for row in results]

    def list_all(self, limit: int = 100) -> list[Lesson]:
        """List all lessons."""
        with duckdb.connect(str(self.db_path)) as conn:
            results = conn.execute(
                "SELECT * FROM lessons ORDER BY number DESC LIMIT ?", [limit]
            ).fetchall()
            return [self._row_to_lesson(row) for row in results]

    def count(self) -> int:
        """Get total lesson count."""
        with duckdb.connect(str(self.db_path)) as conn:
            result = conn.execute("SELECT COUNT(*) FROM lessons").fetchone()
            return result[0] if result else 0

    def get_tags(self) -> list[str]:
        """Get all unique tags."""
        with duckdb.connect(str(self.db_path)) as conn:
            result = conn.execute(
                "SELECT DISTINCT UNNEST(tags) as tag FROM lessons ORDER BY tag"
            ).fetchall()
            return [row[0] for row in result]

    def export_markdown(self) -> str:
        """Export all lessons to markdown format."""
        lessons = self.list_all(limit=1000)
        lines = ["# Development Lessons\n"]

        for lesson in reversed(lessons):  # Oldest first
            lines.append(f"\n---\n")
            lines.append(f"\n## Lesson {lesson.number}: {lesson.title}\n")
            lines.append(f"\n**Date**: {lesson.date_learned}")
            if lesson.project:
                lines.append(f"\n**Project**: {lesson.project}")
            if lesson.context:
                lines.append(f"\n**Context**: {lesson.context}")
            lines.append(f"\n\n### Problem\n\n{lesson.problem}")
            lines.append(f"\n\n### Solution\n\n{lesson.solution}")
            if lesson.checklist:
                lines.append("\n\n### Future Checklist")
                for item in lesson.checklist:
                    lines.append(f"\n- [ ] {item}")
            lines.append("\n")

        return "".join(lines)

    @staticmethod
    def _row_to_lesson(row: tuple) -> Lesson:
        """Convert database row to Lesson model."""
        return Lesson(
            id=row[0],
            number=row[1],
            title=row[2],
            date_learned=row[3],
            project=row[4],
            context=row[5],
            problem=row[6],
            solution=row[7],
            tags=row[8] or [],
            checklist=row[9] or [],
            severity=row[10],
        )
