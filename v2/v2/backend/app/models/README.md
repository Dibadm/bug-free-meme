# Models

SQLAlchemy ORM models.

## Purpose

Defines the database schema using SQLAlchemy 2 declarative mapping.

## Conventions

- All models inherit from `Base`
- UUID primary keys by default
- Timestamp mixins (`created_at`, `updated_at`)
- Soft deletes via `deleted_at` where appropriate
- Relationships use explicit `back_populates`
- Indexes defined for frequently queried columns
- Enums defined as Python enums, mapped to PostgreSQL enums

## Files

- `models.py` - All entity definitions

## Future Models

- Game session models
- Achievement models
- Referral models
- Localization models
