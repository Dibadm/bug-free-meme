# Deployment Notes

## Environment Variables

```bash
# Backend
DATABASE_URL=postgresql+asyncpg://habesha:habesha_secret@db:5432/habesha_bet
REDIS_URL=redis://redis:6379/0
TELEGRAM_BOT_TOKEN=
TELEGRAM_WEB_APP_URL=
TELEGRAM_SECRET_TOKEN=
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080
HOUSE_WALLET_ID=
ADMIN_IDS=
CRYPT_SECRET_KEY=
GAME_ENGINE_HOST=localhost
GAME_ENGINE_PORT=8001

# Frontend
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## Docker Compose

```bash
docker compose up -d
```

## Health Checks

- `GET /health` - Basic health
- `GET /health/live` - Liveness
- `GET /health/ready` - Readiness (DB check)

## Scaling

- Backend: scale horizontally with multiple replicas
- Redis: use Redis Cluster for high availability
- PostgreSQL: use read replicas for analytics

## Monitoring

- Structured logging via structlog
- Health check endpoints
- WebSocket connection stats
- Background worker health

## Backup

- Daily PostgreSQL backups
- Redis persistence enabled
- Audit log archiving

## Security

- HTTPS required in production
- CORS restricted to configured origins
- Rate limiting enabled
- Security headers enforced
