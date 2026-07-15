# Tests

Backend test suite.

## Purpose

Contains all backend unit, integration, and e2e tests.

## Structure

- `conftest.py` - Shared pytest fixtures
- `fixtures/` - Test data factories
- `unit/` - Unit tests for services and utilities
- `integration/` - Database integration tests
- `e2e/` - End-to-end API tests

## Running Tests

```bash
cd backend
pytest tests/ -v
```

## Coverage

```bash
cd backend
pytest --cov=app tests/
```
