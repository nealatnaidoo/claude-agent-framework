"""Data models for lessons."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Lesson(BaseModel):
    """A development lesson learned."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "number": 124,
                "title": "Grep Patterns Must Match All Heading Variations",
                "date_learned": "2026-02-04",
                "project": "claude-agent-framework",
                "context": "/learn command reporting wrong count",
                "problem": "Grep pattern ^### Lesson only matched 3-hash headings",
                "solution": "Use ^##+ to match all heading levels",
                "tags": ["grep", "regex", "markdown"],
                "checklist": ["Use ^##+ for markdown headings", "Test patterns against actual data"],
                "severity": "medium",
            }
        }
    )

    id: int = Field(default=0, description="Unique lesson ID")
    number: Optional[int] = Field(default=None, description="Lesson number (e.g., 124)")
    title: str = Field(..., description="Lesson title")
    date_learned: date = Field(default_factory=date.today, description="Date lesson was learned")
    project: Optional[str] = Field(default=None, description="Project where lesson was learned")
    context: Optional[str] = Field(default=None, description="Brief context")
    problem: str = Field(..., description="Problem description")
    solution: str = Field(..., description="Solution description")
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")
    checklist: list[str] = Field(default_factory=list, description="Future checklist items")
    severity: str = Field(default="medium", description="Severity: low, medium, high, critical")


class LessonCreate(BaseModel):
    """Input for creating a new lesson."""

    title: str
    problem: str
    solution: str
    project: Optional[str] = None
    context: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    checklist: list[str] = Field(default_factory=list)
    severity: str = "medium"
