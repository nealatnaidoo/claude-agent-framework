# Hexagonal Architecture Reference

**Source**: devlessons.md - Lessons 4, 8, 12, 24, 79, 87, 100, 103, 107
**Version**: 1.0
**Date**: 2026-01-31

---

## Core Principles

> **Lesson #4**: Clean architecture pays dividends during migrations

### The Rule

```
Core/Domain code MUST NOT depend on infrastructure.
Infrastructure code MUST depend on Core/Domain.
```

### Layer Diagram

```
                    ┌─────────────────────────────────────────────┐
                    │              ADAPTERS (Infrastructure)       │
                    │  ┌─────────┐  ┌─────────┐  ┌─────────────┐  │
                    │  │ FastAPI │  │ SQLite  │  │   Requests  │  │
                    │  │ Routes  │  │ Adapter │  │   Adapter   │  │
                    │  └────┬────┘  └────┬────┘  └──────┬──────┘  │
                    │       │            │              │          │
                    └───────┼────────────┼──────────────┼──────────┘
                            │            │              │
                    ┌───────▼────────────▼──────────────▼──────────┐
                    │                  PORTS (Interfaces)           │
                    │  ┌────────────┐  ┌────────────┐  ┌─────────┐ │
                    │  │ RouterPort │  │ RepoPort   │  │ APIPort │ │
                    │  └─────┬──────┘  └─────┬──────┘  └────┬────┘ │
                    └────────┼───────────────┼──────────────┼──────┘
                             │               │              │
                    ┌────────▼───────────────▼──────────────▼──────┐
                    │              CORE / DOMAIN                    │
                    │  ┌────────────┐  ┌────────────┐              │
                    │  │  Entities  │  │  Services  │              │
                    │  │  (Models)  │  │ (Use Cases)│              │
                    │  └────────────┘  └────────────┘              │
                    │                                              │
                    │  NO FRAMEWORK IMPORTS ALLOWED HERE           │
                    └──────────────────────────────────────────────┘
```

---

## Directory Structure

```
src/
├── domain/                    # Pure Python, NO I/O
│   ├── entities/              # Business objects (dataclasses)
│   ├── policies/              # Business rules (pure functions)
│   ├── types.py               # Shared Literal types, enums
│   └── ports.py               # Protocol interfaces
│
├── services/                  # Use cases (orchestration)
│   ├── content_service.py     # Depends on ports, not adapters
│   └── publish_service.py
│
├── adapters/                  # Infrastructure implementations
│   ├── repositories/
│   │   ├── sqlite_repo.py     # Implements RepositoryPort
│   │   └── postgres_repo.py
│   ├── external/
│   │   ├── stripe_adapter.py  # Implements PaymentPort
│   │   └── sendgrid_adapter.py
│   └── time_adapter.py        # Implements TimePort
│
├── components/                # Atomic components (self-contained)
│   └── {ComponentName}/
│       ├── component.py       # run() entry point
│       ├── models.py          # Frozen dataclasses
│       ├── ports.py           # Local protocol interfaces
│       ├── contract.md        # Specification
│       └── __init__.py        # Public exports
│
└── api/                       # HTTP layer (depends on services)
    ├── routes/
    │   ├── content_routes.py
    │   └── auth_routes.py
    └── schemas.py             # Pydantic request/response models
```

---

## Forbidden Imports in Core

> **Lesson #100**: Hexagonal architecture for external C++ libraries

The following imports are **FORBIDDEN** in `src/domain/` and `src/*/core/`:

| Forbidden Import | Why | Alternative |
|------------------|-----|-------------|
| `fastapi` | Web framework | Define RouterPort protocol |
| `sqlalchemy` | ORM | Define RepositoryPort protocol |
| `requests` / `httpx` | HTTP client | Define APIPort protocol |
| `datetime.now()` | Non-deterministic | Inject TimePort (Lesson #107) |
| `uuid4()` | Non-deterministic | Inject UUIDPort (Lesson #107) |
| `random.*` | Non-deterministic | Inject RandomPort |
| `os.environ` | Configuration | Inject ConfigPort |
| Any database driver | Infrastructure | Define RepositoryPort |

### Detection Command

```bash
# Check for forbidden imports in core
grep -r "from fastapi\|from sqlalchemy\|import requests\|import httpx" src/domain/ src/*/core/
# Should return nothing

# Check for determinism violations
grep -r "datetime\.now\|datetime\.utcnow\|uuid4\|random\." src/domain/ src/*/core/ --include="*.py" | grep -v import
# Should return nothing
```

---

## Port Patterns

### Protocol-Based Ports (Lesson #107)

```python
# src/domain/ports.py
from typing import Protocol
from datetime import datetime

class TimePort(Protocol):
    """All time operations go through this port."""
    def now(self) -> datetime:
        ...

class UUIDPort(Protocol):
    """All UUID generation goes through this port."""
    def generate(self) -> str:
        ...

class RepositoryPort(Protocol):
    """Data persistence abstraction."""
    def get(self, id: str) -> dict | None:
        ...
    def save(self, id: str, data: dict) -> None:
        ...
    def delete(self, id: str) -> bool:
        ...
```

### Adapter Implementations

```python
# src/adapters/time_adapter.py
from datetime import datetime, timezone

class SystemTimeAdapter:
    """Production implementation - uses real time."""
    def now(self) -> datetime:
        return datetime.now(timezone.utc)

# For testing
class FakeTimeAdapter:
    """Test implementation - uses fixed time."""
    def __init__(self, fixed_time: datetime) -> None:
        self._time = fixed_time

    def now(self) -> datetime:
        return self._time
```

---

## Dependency Injection Pattern

### Service Constructor

```python
# src/services/content_service.py
from src.domain.ports import RepositoryPort, TimePort

class ContentService:
    """Service depends on ports, not concrete implementations."""

    def __init__(
        self,
        repository: RepositoryPort,
        time_port: TimePort,
    ) -> None:
        self._repo = repository
        self._time = time_port

    def create_content(self, title: str, body: str) -> dict:
        # Uses injected ports
        content = {
            "id": str(uuid.uuid4()),  # Should also be injected!
            "title": title,
            "body": body,
            "created_at": self._time.now().isoformat(),
        }
        self._repo.save(content["id"], content)
        return content
```

### Wiring at Application Boundary

```python
# src/main.py (or composition root)
from src.services.content_service import ContentService
from src.adapters.repositories.sqlite_repo import SQLiteRepository
from src.adapters.time_adapter import SystemTimeAdapter

# Wire dependencies at the edge
repository = SQLiteRepository(db_path="/data/app.db")
time_adapter = SystemTimeAdapter()

content_service = ContentService(
    repository=repository,
    time_port=time_adapter,
)

# Now content_service is ready to use
```

---

## Testing Benefits

### Unit Testing with Fakes

```python
# tests/unit/test_content_service.py
from src.services.content_service import ContentService
from datetime import datetime, timezone

class FakeRepository:
    def __init__(self):
        self._data = {}

    def get(self, id: str) -> dict | None:
        return self._data.get(id)

    def save(self, id: str, data: dict) -> None:
        self._data[id] = data

class FakeTimeAdapter:
    def __init__(self, fixed_time: datetime):
        self._time = fixed_time

    def now(self) -> datetime:
        return self._time

def test_create_content():
    # Arrange - deterministic setup
    fixed_time = datetime(2026, 1, 31, 12, 0, 0, tzinfo=timezone.utc)
    repo = FakeRepository()
    time_adapter = FakeTimeAdapter(fixed_time)
    service = ContentService(repository=repo, time_port=time_adapter)

    # Act
    result = service.create_content("Test Title", "Test Body")

    # Assert - deterministic verification
    assert result["title"] == "Test Title"
    assert result["created_at"] == "2026-01-31T12:00:00+00:00"  # Predictable!
    assert repo.get(result["id"]) is not None
```

---

## Extension Pattern (Lesson #103)

> **Extend, don't modify core**

When adding new functionality:

1. **Create new port** if new dependency type
2. **Create new adapter** implementing the port
3. **Inject** at composition root
4. **Never modify** existing core logic

```python
# Adding caching - create new port
class CachePort(Protocol):
    def get(self, key: str) -> Any | None: ...
    def set(self, key: str, value: Any, ttl: int) -> None: ...

# Create adapter
class RedisCacheAdapter:
    def __init__(self, redis_client): ...
    def get(self, key: str) -> Any | None: ...
    def set(self, key: str, value: Any, ttl: int) -> None: ...

# Inject into service
class ContentService:
    def __init__(
        self,
        repository: RepositoryPort,
        time_port: TimePort,
        cache: CachePort | None = None,  # Optional extension
    ): ...
```

---

## Migration Benefits (Lesson #4)

When the Little Research Lab migrated from Flet to React:

| Layer | What Changed |
|-------|--------------|
| `src/domain/` | **NOTHING** - Pure Python |
| `src/services/` | **NOTHING** - Business logic |
| `src/ports/` | **NOTHING** - Interfaces |
| `src/adapters/` | **NOTHING** - Same implementations |
| `src/app_shell/` | **REPLACED** - Flet → FastAPI |
| `frontend/` | **REPLACED** - Flet → React |

**Result**: Complete UI framework change with zero changes to business logic.

---

## Checklist

### For New Components

- [ ] Does core code depend only on ports?
- [ ] Are all dependencies injected, not imported?
- [ ] Is there no `datetime.now()`, `uuid4()`, `random` in core?
- [ ] Can the component be tested with fakes?
- [ ] Is the contract defined before implementation?

### For Code Review

- [ ] No framework imports in domain/core
- [ ] All I/O goes through ports
- [ ] Dependencies injected at composition root
- [ ] Test doubles match production signatures
- [ ] No determinism violations

### For Architecture Validation

```bash
# Run this to check hexagonal compliance
grep -r "from fastapi\|from sqlalchemy\|datetime\.now\|uuid4" src/domain/ src/*/core/ --include="*.py"
# Should return NOTHING
```
