# Backend Hexagonal Architecture Pattern

## Overview

This pattern enforces hexagonal architecture (ports & adapters) for all Python backend code. The domain is sacred. Infrastructure is replaceable. The boundary between them is enforced by port interfaces.

## Canonical Component Structure

```
components/
  <component_name>/
    domain/
      __init__.py
      model.py            # Entities, value objects, enums
      service.py          # Business logic — orchestrates domain operations
      events.py           # Domain events (optional)
      exceptions.py       # Domain-specific exceptions
      rules.py            # Business rules / validation (optional)
    ports/
      __init__.py
      inbound.py          # Driving port interfaces (ABC classes)
      outbound.py         # Driven port interfaces (ABC classes)
    adapters/
      __init__.py
      inbound/
        __init__.py
        api_handler.py    # HTTP/REST entry points
        cli.py            # CLI entry points (optional)
        event_consumer.py # Message queue consumers (optional)
      outbound/
        __init__.py
        postgres_repo.py  # Concrete repository implementation
        memory_repo.py    # In-memory implementation for testing
        http_client.py    # External service clients (optional)
    tests/
      __init__.py
      unit/
        test_model.py     # Pure domain model tests
        test_service.py   # Service tests with in-memory adapters
      integration/
        test_api.py       # API handler integration tests
        test_repo.py      # Repository against real DB
      regression/
        test_*.py         # Bug reproduction tests — NEVER DELETE
      conftest.py         # Fixtures: in-memory adapters, factories
    README.md             # Component purpose, ports summary
    __init__.py           # Public API — ONLY re-exports
```

## Dependency Direction (INVIOLABLE)

```
ALLOWED:
  adapters/inbound  → ports/inbound, domain/*
  adapters/outbound → ports/outbound, domain/model, domain/exceptions
  domain/service    → ports/outbound (interfaces only), domain/*
  domain/model      → standard library, shared kernel ONLY

FORBIDDEN:
  domain/*          → adapters/* (domain must NEVER know infrastructure)
  domain/model      → ANY external library (no SQLAlchemy, no Pydantic)
  ports/*           → adapters/*
  adapters/inbound  → adapters/outbound
```

## Files Included

| File | Purpose |
|------|---------|
| `pyproject.toml` | Ruff, mypy, pytest, coverage configuration |
| `.importlinter` | Import boundary enforcement rules |
| `hex_audit.py` | Structure validation script |

## Usage

1. Copy configuration files to your project root
2. Install dependencies: `pip install ruff mypy pytest import-linter`
3. Run quality gates:
   ```bash
   ruff check components/ --fix
   python -m mypy components/
   python -m importlinter
   python hex_audit.py components/
   pytest components/ -m unit
   ```

## Violation Codes

| Code | Rule |
|------|------|
| HEX001 | Missing required directory |
| HEX002 | Missing required file |
| HEX003 | Port class not inheriting ABC |
| HEX004 | Port method not @abstractmethod |
| HEX005 | Port method missing return type |
| HEX006 | No in-memory adapter for infrastructure adapter |
| HEX007 | Domain model imports forbidden framework |
| HEX008 | No unit tests |
| HEX009 | No integration tests |
| HEX010 | Syntax error in file |
