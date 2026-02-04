"""Import lessons from existing devlessons.md file."""

import re
from datetime import date
from pathlib import Path

from claude_cli.lessons.db import LessonsDB
from claude_cli.lessons.models import LessonCreate


def import_from_markdown(file_path: str) -> int:
    """Import lessons from a markdown file.

    Returns:
        Number of lessons imported.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    content = path.read_text()
    lessons = parse_lessons(content)

    db = LessonsDB()
    count = 0

    for lesson_data in lessons:
        try:
            db.add(lesson_data)
            count += 1
        except Exception as e:
            print(f"Warning: Failed to import lesson '{lesson_data.title}': {e}")

    return count


def parse_lessons(content: str) -> list[LessonCreate]:
    """Parse lessons from markdown content."""
    lessons = []

    # Pattern matches both ## Lesson and ### Lesson formats
    lesson_pattern = re.compile(
        r'^##+ Lesson\s*(\d+)?[:\s]*(.+?)$',
        re.MULTILINE
    )

    # Split content by lesson headers
    parts = lesson_pattern.split(content)

    # Parts will be: [preamble, num1, title1, content1, num2, title2, content2, ...]
    i = 1
    while i < len(parts) - 2:
        number_str = parts[i]
        title = parts[i + 1].strip()
        body = parts[i + 2] if i + 2 < len(parts) else ""

        lesson = parse_lesson_body(title, body, number_str)
        if lesson:
            lessons.append(lesson)

        i += 3

    return lessons


def parse_lesson_body(title: str, body: str, number_str: str | None) -> LessonCreate | None:
    """Parse a single lesson's body content."""
    if not title or not body.strip():
        return None

    # Extract date
    date_match = re.search(r'\*\*Date\*\*[:\s]*(\d{4}-\d{2}-\d{2})', body)
    lesson_date = date_match.group(1) if date_match else None

    # Extract project
    project_match = re.search(r'\*\*(?:Project|Context)\*\*[:\s]*([^\n]+)', body)
    project = project_match.group(1).strip() if project_match else None

    # Extract context (different from project)
    context_match = re.search(r'\*\*Context\*\*[:\s]*([^\n]+)', body)
    context = context_match.group(1).strip() if context_match else None

    # Extract problem section
    problem = extract_section(body, ["Problem", "What happened"])

    # Extract solution section
    solution = extract_section(body, ["Solution", "The fix"])

    # Extract checklist items
    checklist = extract_checklist(body)

    # Extract tags from content (heuristic)
    tags = extract_tags(title, body)

    if not problem or not solution:
        # Try simpler extraction for older format
        problem = problem or body[:500]
        solution = solution or "See lesson body"

    return LessonCreate(
        title=title,
        problem=problem,
        solution=solution,
        project=project,
        context=context,
        tags=tags,
        checklist=checklist,
        severity="medium",
    )


def extract_section(body: str, headers: list[str]) -> str:
    """Extract a section by header name."""
    for header in headers:
        # Try ### Header format
        pattern = rf'###\s*{header}[:\s]*\n(.*?)(?=\n###|\n##|\Z)'
        match = re.search(pattern, body, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Try **Header:** format
        pattern = rf'\*\*{header}[:\s]*\*\*[:\s]*\n?(.*?)(?=\n\*\*|\n###|\n##|\Z)'
        match = re.search(pattern, body, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return ""


def extract_checklist(body: str) -> list[str]:
    """Extract checklist items from body."""
    items = []
    pattern = r'- \[[ x]\]\s*(.+)'
    for match in re.finditer(pattern, body):
        items.append(match.group(1).strip())
    return items


def extract_tags(title: str, body: str) -> list[str]:
    """Extract likely tags from content."""
    tags = set()

    # Common technology keywords
    keywords = {
        "python": ["python", "pytest", "pydantic", "fastapi"],
        "javascript": ["javascript", "typescript", "react", "next.js", "node"],
        "testing": ["test", "pytest", "playwright", "e2e"],
        "database": ["database", "sql", "duckdb", "postgres", "sqlite"],
        "docker": ["docker", "container", "dockerfile"],
        "git": ["git", "commit", "branch", "worktree"],
        "api": ["api", "endpoint", "rest", "graphql"],
        "architecture": ["hexagonal", "architecture", "ports", "adapters"],
        "deployment": ["deploy", "fly.io", "ci/cd", "pipeline"],
    }

    text = (title + " " + body).lower()

    for tag, patterns in keywords.items():
        for pattern in patterns:
            if pattern in text:
                tags.add(tag)
                break

    return list(tags)
