# Claude Agent Framework CLI

Command-line tools for managing the Claude Agent Framework.

## Installation

```bash
# From the cli directory
cd cli
pip install -e .

# Or with uv
uv pip install -e .
```

## Usage

```bash
# Show help
claude --help

# Show framework status
claude status

# Show version
claude version
```

## Commands

### Lessons Management

```bash
# Add a new lesson
claude lessons add "Title" --problem "..." --solution "..."

# Search lessons
claude lessons search "testing"
claude lessons search --tag python --since 2026-01-01

# List all lessons
claude lessons list --limit 50

# Show lesson details
claude lessons show 124

# Export to markdown
claude lessons export --output lessons.md

# Import from existing devlessons.md
claude lessons import-markdown ~/.claude/knowledge/devlessons.md

# Show statistics
claude lessons stats

# List all tags
claude lessons tags
```

### Agent Management

```bash
# List all agents
claude agents list

# Validate agents
claude agents validate
claude agents validate my-agent

# Create new agent
claude agents new my-agent --type micro

# Show agent details
claude agents show business-analyst
```

### Worktree Management

```bash
# List worktrees
claude worktree list

# Create feature worktree
claude worktree create user-auth --base main

# Remove worktree
claude worktree remove ../project-user-auth

# Sync artifacts to worktree
claude worktree sync ../project-user-auth

# Show worktree status
claude worktree status
```

### Database Harness (DevOps)

```bash
# Schema drift detection
claude db drift --source "postgres://dev" --target "postgres://staging"

# Foreign key integrity check
claude db fk-check --connection "postgres://..."

# PII masking (dry run)
claude db mask --connection "postgres://..." --dry-run

# PII masking (apply)
claude db mask --connection "postgres://..." --apply

# View audit trail
claude db audit --connection "postgres://..." --since 2026-01-01

# Validate migration file
claude db validate migrations/001_add_users.sql
```

## Database Files

CLI databases are stored in `cli/data/`:
- `lessons.duckdb` - Development lessons database

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy claude_cli

# Linting
ruff check claude_cli
```

## Architecture

```
cli/
├── pyproject.toml          # Package definition
├── claude_cli/
│   ├── main.py             # Root CLI entry point
│   ├── lessons/            # Lessons management
│   │   ├── cli.py          # Commands
│   │   ├── db.py           # DuckDB operations
│   │   ├── models.py       # Pydantic models
│   │   └── importer.py     # Markdown import
│   ├── agents/             # Agent management
│   │   └── cli.py          # Commands
│   ├── worktree/           # Git worktree management
│   │   └── cli.py          # Commands
│   ├── db/                 # Database harness (DevOps)
│   │   ├── cli.py          # Commands
│   │   ├── drift.py        # Schema drift detection
│   │   ├── integrity.py    # FK integrity checks
│   │   ├── masking.py      # PII masking
│   │   └── audit.py        # Audit trail
│   └── common/             # Shared utilities
│       ├── config.py       # Path configuration
│       └── db.py           # DuckDB connection
└── data/                   # Database files
    └── lessons.duckdb
```
