# V1

API version 1 routes.

## Purpose

Contains all v1 endpoint definitions, schemas, and business logic adapters.

## Files

- `router.py` - Aggregates all v1 sub-routers
- `auth.py` - Telegram auth validation
- `users.py` - User CRUD and profiles
- `rooms.py` - Room template management
- `games.py` - Game lifecycle endpoints
- `wallet.py` - Deposit, withdrawal, transfer
- `admin.py` - Admin dashboard and controls

## Dependencies

- app.core.database
- app.schemas.*
- app.services.*
