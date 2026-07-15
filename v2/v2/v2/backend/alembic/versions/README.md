# Versions

Alembic migration files.

## Purpose

Stores individual migration scripts in chronological order.

## Naming

Format: `<revision_id>_<description>.py`

Example: `a1b2c3d4_add_wallet_table.py`

## Guidelines

- One logical change per migration
- Test both upgrade and downgrade
- Include data migrations when schema changes require it
