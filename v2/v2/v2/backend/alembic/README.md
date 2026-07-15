# Alembic

Database migration framework.

## Purpose

Manages database schema versioning and migrations.

## Usage

```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1
```

## Configuration

- `alembic.ini` or `pyproject.toml` - Alembic config
- `script.py.mako` - Migration template
- `versions/` - Migration files

## Conventions

- Migrations are named descriptively: `add_user_table.py`
- Always include `downgrade()` even if no-op
- Never modify committed migrations
