"""CLI commands for lessons management."""

from datetime import date
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from claude_cli.lessons.db import LessonsDB
from claude_cli.lessons.models import LessonCreate

app = typer.Typer(help="Manage development lessons")
console = Console()


@app.command()
def add(
    title: str = typer.Argument(..., help="Lesson title"),
    problem: str = typer.Option(..., "--problem", "-p", help="Problem description"),
    solution: str = typer.Option(..., "--solution", "-s", help="Solution description"),
    project: Optional[str] = typer.Option(None, "--project", help="Project name"),
    context: Optional[str] = typer.Option(None, "--context", "-c", help="Brief context"),
    tags: Optional[str] = typer.Option(None, "--tags", "-t", help="Comma-separated tags"),
    severity: str = typer.Option("medium", "--severity", help="low/medium/high/critical"),
) -> None:
    """Add a new lesson to the database."""
    db = LessonsDB()

    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    lesson = LessonCreate(
        title=title,
        problem=problem,
        solution=solution,
        project=project,
        context=context,
        tags=tag_list,
        severity=severity,
    )

    result = db.add(lesson)
    console.print(f"\n[green]✓[/green] Added Lesson {result.number}: {result.title}\n")


@app.command()
def search(
    query: Optional[str] = typer.Argument(None, help="Search query"),
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Filter by tag"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Filter by project"),
    severity: Optional[str] = typer.Option(None, "--severity", "-s", help="Filter by severity"),
    since: Optional[str] = typer.Option(None, "--since", help="Since date (YYYY-MM-DD)"),
    limit: int = typer.Option(20, "--limit", "-n", help="Max results"),
) -> None:
    """Search lessons with filters."""
    db = LessonsDB()

    tags = [tag] if tag else None
    since_date = date.fromisoformat(since) if since else None

    lessons = db.search(
        query=query,
        tags=tags,
        project=project,
        severity=severity,
        since=since_date,
        limit=limit,
    )

    if not lessons:
        console.print("\n[yellow]No lessons found matching criteria.[/yellow]\n")
        return

    _display_lessons_table(lessons)


@app.command("list")
def list_lessons(
    limit: int = typer.Option(20, "--limit", "-n", help="Max results"),
) -> None:
    """List all lessons."""
    db = LessonsDB()
    lessons = db.list_all(limit=limit)

    if not lessons:
        console.print("\n[yellow]No lessons in database.[/yellow]\n")
        return

    _display_lessons_table(lessons)


@app.command()
def show(
    number: int = typer.Argument(..., help="Lesson number"),
) -> None:
    """Show full details of a lesson."""
    db = LessonsDB()
    lesson = db.get(number)

    if not lesson:
        console.print(f"\n[red]Lesson {number} not found.[/red]\n")
        raise typer.Exit(1)

    console.print(f"\n[bold]Lesson {lesson.number}: {lesson.title}[/bold]")
    console.print(f"Date: {lesson.date_learned}")
    if lesson.project:
        console.print(f"Project: {lesson.project}")
    if lesson.context:
        console.print(f"Context: {lesson.context}")
    console.print(f"Severity: {lesson.severity}")
    if lesson.tags:
        console.print(f"Tags: {', '.join(lesson.tags)}")

    console.print("\n[bold]Problem:[/bold]")
    console.print(lesson.problem)

    console.print("\n[bold]Solution:[/bold]")
    console.print(lesson.solution)

    if lesson.checklist:
        console.print("\n[bold]Future Checklist:[/bold]")
        for item in lesson.checklist:
            console.print(f"  - [ ] {item}")

    console.print()


@app.command()
def tags() -> None:
    """List all tags."""
    db = LessonsDB()
    all_tags = db.get_tags()

    if not all_tags:
        console.print("\n[yellow]No tags found.[/yellow]\n")
        return

    console.print("\n[bold]Available Tags:[/bold]\n")
    for tag in all_tags:
        console.print(f"  • {tag}")
    console.print()


@app.command()
def stats() -> None:
    """Show lesson statistics."""
    db = LessonsDB()

    count = db.count()
    all_tags = db.get_tags()

    console.print("\n[bold]Lessons Statistics[/bold]\n")
    console.print(f"  Total lessons: {count}")
    console.print(f"  Unique tags: {len(all_tags)}")
    console.print()


@app.command()
def export(
    format: str = typer.Option("markdown", "--format", "-f", help="Export format (markdown)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """Export lessons to markdown."""
    db = LessonsDB()

    if format != "markdown":
        console.print(f"\n[red]Unsupported format: {format}[/red]\n")
        raise typer.Exit(1)

    content = db.export_markdown()

    if output:
        with open(output, "w") as f:
            f.write(content)
        console.print(f"\n[green]✓[/green] Exported to {output}\n")
    else:
        console.print(content)


@app.command()
def import_markdown(
    file: str = typer.Argument(..., help="Path to devlessons.md"),
) -> None:
    """Import lessons from existing devlessons.md file."""
    from claude_cli.lessons.importer import import_from_markdown

    count = import_from_markdown(file)
    console.print(f"\n[green]✓[/green] Imported {count} lessons\n")


def _display_lessons_table(lessons: list) -> None:
    """Display lessons in a table."""
    table = Table(title="Lessons")
    table.add_column("#", style="cyan", width=5)
    table.add_column("Title", style="white", max_width=50)
    table.add_column("Date", style="green", width=12)
    table.add_column("Project", style="yellow", width=20)
    table.add_column("Severity", style="magenta", width=10)

    for lesson in lessons:
        table.add_row(
            str(lesson.number),
            lesson.title[:47] + "..." if len(lesson.title) > 50 else lesson.title,
            str(lesson.date_learned),
            (lesson.project or "-")[:17] + "..." if lesson.project and len(lesson.project) > 20 else (lesson.project or "-"),
            lesson.severity,
        )

    console.print()
    console.print(table)
    console.print()
