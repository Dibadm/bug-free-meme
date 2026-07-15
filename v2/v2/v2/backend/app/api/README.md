# API

API route definitions.

## Purpose

Organizes all API endpoints by version and domain.

## Structure

- `v1/` - Version 1 API routes
  - `router.py` - Main v1 router aggregator
  - `auth.py` - Authentication endpoints
  - `users.py` - User management
  - `rooms.py` - Room templates and instances
  - `games.py` - Game sessions and state
  - `wallet.py` - Wallet operations
  - `admin.py` - Admin-only endpoints

## Future Versions

- `v2/` - Future API version with breaking changes

## Conventions

- All routes return standardized response envelopes
- Errors use consistent format
- Pagination uses cursor-based strategy
- All mutations require authentication
