# Backend

FastAPI application powering the Habesha Bet V2 platform.

## Purpose

Provides RESTful APIs for:
- User authentication and management
- Game state management
- Wallet operations
- Admin operations
- Telegram bot integration

## Responsibilities

- API routing and versioning
- Request validation and serialization
- Database session management
- Business logic orchestration
- Security and authentication
- Audit logging

## Dependencies

- FastAPI
- SQLAlchemy 2 (async)
- Alembic (migrations)
- Pydantic v2
- python-telegram-bot
- Redis (caching/pub-sub)
- PostgreSQL (primary database)

## Future Modules

- `app/game/` - Game session orchestration
- `app/bot/` - Telegram bot handlers
- `app/tasks/` - Background workers
- `app/middleware/` - Custom middleware
- `app/exceptions/` - Exception handlers
