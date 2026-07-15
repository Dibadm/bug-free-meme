# Core

Core application infrastructure.

## Purpose

Provides foundational services used throughout the application.

## Modules

- `config.py` - Environment-based configuration with Pydantic Settings
- `database.py` - Async SQLAlchemy engine and session management
- `logging.py` - Structured logging configuration
- `security.py` - Authentication and authorization utilities
- `exceptions.py` - Custom exception classes and handlers
- `middleware.py` - Custom middleware (CORS, logging, rate limiting)

## Dependencies

- pydantic-settings
- sqlalchemy
- structlog
- python-jose
- passlib
