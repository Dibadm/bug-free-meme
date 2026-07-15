# Adapters

External integration adapters.

## Purpose

Isolates third-party integrations behind clean interfaces.

## Modules

- `telegram.py` - Telegram Web App init data validation
- `payment.py` - Payment provider integrations (future)

## Conventions

- Adapters do not contain business logic
- Adapters translate external formats to internal models
- Adapters raise integration-specific exceptions
