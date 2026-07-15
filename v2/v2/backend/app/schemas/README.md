# Schemas

Pydantic request/response schemas.

## Purpose

Defines validation and serialization contracts for all API endpoints.

## Conventions

- BaseSchema provides `from_attributes=True` for ORM serialization
- Create schemas for input validation
- Read schemas for output serialization
- Update schemas for partial updates
- Generic `Page[T]` for paginated responses

## Files

- `__init__.py` - Base schema and pagination
- `common.py` - Shared schemas (User, Wallet, RoomTemplate)
- `game.py` - Game-specific schemas
- `wallet.py` - Wallet operation schemas
- `admin.py` - Admin-specific schemas
