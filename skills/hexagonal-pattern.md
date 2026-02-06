---
description: Apply hexagonal architecture pattern to a Python backend component
---

<hexagonal-pattern>

## Hexagonal Architecture Pattern

Apply this pattern when creating or validating Python backend components.

### Component Structure

```
components/<name>/
  domain/
    model.py            # Entities, value objects, enums (NO external libs)
    service.py          # Business logic (depends only on ports)
    exceptions.py       # Domain-specific exceptions
  ports/
    inbound.py          # Driving port interfaces (ABC classes)
    outbound.py         # Driven port interfaces (ABC classes)
  adapters/
    inbound/
      api_handler.py    # HTTP/REST entry points
    outbound/
      postgres_repo.py  # Concrete repository
      memory_repo.py    # In-memory for testing (REQUIRED)
  tests/
    unit/test_model.py, test_service.py
    integration/test_api.py, test_repo.py
```

### Dependency Rules (INVIOLABLE)

- `domain/*` MUST NOT import `adapters/*` or any framework
- `domain/model` MUST NOT use SQLAlchemy, Pydantic BaseModel, or external libs
- `domain/service` depends ONLY on `ports/outbound` interfaces + `domain/*`
- Every outbound adapter MUST have a corresponding `memory_*.py` for tests
- All ports MUST be ABC classes with `@abstractmethod` decorators

### Determinism Rules

- No `datetime.now()` in domain - inject via `TimePort`
- No `uuid4()` in domain - inject via `UUIDPort`
- No `random.*` in domain - inject via `RandomPort`

### Quality Gates

```bash
ruff check components/ --fix
python -m mypy components/
python hex_audit.py components/
pytest components/ -m unit
```

Full pattern reference: `~/.claude/patterns/backend-hexagonal/`
Audit tool: `~/.claude/patterns/backend-hexagonal/hex_audit.py`

</hexagonal-pattern>
