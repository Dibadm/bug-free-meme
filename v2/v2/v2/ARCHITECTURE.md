# Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Telegram Client                        │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                        Nginx (80/443)                        │
│  ┌──────────────┐                              ┌───────────┐ │
│  │ /api/        │                              │ /         │ │
│  │ → backend    │                              │ → frontend │ │
│  └──────────────┘                              └───────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                ▼                               ▼
    ┌──────────────────────┐         ┌──────────────────┐
    │      Backend         │         │     Frontend     │
    │   FastAPI + Python   │         │   React + TS     │
    │                      │         │                  │
    │  ┌──────────────┐   │         │  ┌────────────┐  │
    │  │ API v1       │   │         │  │ Pages      │  │
    │  ├──────────────┤   │         │  ├────────────┤  │
    │  │ Services     │   │         │  │ Components │  │
    │  ├──────────────┤   │         │  ├────────────┤  │
    │  │ Models       │◄──┼─────────┼─►│ Hooks      │  │
    │  └──────────────┘   │         │  └────────────┘  │
    │         ▲           │         │                  │
    │         │           │         │  ┌────────────┐  │
    │  ┌──────┴───────┐   │         │  │ Providers  │  │
    │  │ Game Engine  │   │         │  └────────────┘  │
    │  │ (Standalone) │   │         │                  │
    │  └──────────────┘   │         └──────────────────┘
    └──────────┬──────────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
┌──────────┐      ┌──────────┐
│PostgreSQL│      │  Redis   │
└──────────┘      └──────────┘
```

## Backend Architecture

- **API Layer** (`app/api/v1/`) - Route definitions and request handling
- **Service Layer** (`app/services/`) - Business logic
- **Model Layer** (`app/models/`) - SQLAlchemy ORM
- **Adapter Layer** (`app/adapters/`) - External integrations
- **Core Layer** (`app/core/`) - Infrastructure (config, logging, security)

## Frontend Architecture

- **Pages** (`src/pages/`) - Route components
- **Components** (`src/components/`) - Reusable UI components
- **Hooks** (`src/hooks/`) - Custom React hooks
- **Lib** (`src/lib/`) - Utilities, API client, providers
- **Styles** (`src/styles/`) - Global styles and tokens

## Game Engine Architecture

- **Framework-agnostic** - Zero FastAPI/React dependencies
- **Deterministic** - Seed-based RNG
- **Verifiable** - Cryptographic hash commitments
- **Crash-recoverable** - Serializable state
- **Extensible** - Plugin-based pattern system

## Data Flow

1. User opens Telegram Mini App
2. Telegram sends `initData` to frontend
3. Frontend validates and sends to backend `/auth/validate`
4. Backend creates/updates user, returns JWT
5. Frontend stores token and fetches rooms/games
6. Game engine manages live game state
7. Backend persists all state changes to PostgreSQL
8. Frontend subscribes to game updates via polling/WebSocket

## Security

- Telegram init data validation (HMAC-SHA256)
- JWT access tokens
- CORS restricted to configured origins
- Rate limiting per IP
- Structured audit logging
- No secrets in code (env vars only)
