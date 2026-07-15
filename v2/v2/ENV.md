# Environment Variables

## Backend

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DEBUG` | Enable debug mode | No | `false` |
| `DATABASE_URL` | PostgreSQL async connection string | Yes | - |
| `REDIS_URL` | Redis connection string | No | `redis://localhost:6379/0` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token from @BotFather | Yes | - |
| `TELEGRAM_WEB_APP_URL` | Public URL of the Telegram Mini App | Yes | - |
| `TELEGRAM_SECRET_TOKEN` | Secret for Telegram webhook validation | Yes | - |
| `JWT_SECRET_KEY` | Secret key for JWT signing | Yes | - |
| `JWT_ALGORITHM` | JWT signing algorithm | No | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | JWT expiration time | No | `10080` |
| `HOUSE_WALLET_ID` | UUID of the house wallet | Yes | - |
| `ADMIN_IDS` | Comma-separated admin Telegram IDs | No | - |
| `CRYPT_SECRET_KEY` | Fernet key for encryption | Yes | - |
| `CRYPT_ALGORITHM` | Encryption algorithm | No | `Fernet` |
| `GAME_ENGINE_HOST` | Game engine host | No | `localhost` |
| `GAME_ENGINE_PORT` | Game engine port | No | `8001` |

## Frontend

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `VITE_API_URL` | Backend API URL | No | `http://localhost:8000` |

## Development

```bash
# Backend
export DEBUG=true
export DATABASE_URL=postgresql+asyncpg://habesha:habesha_secret@localhost:5432/habesha_bet
export JWT_SECRET_KEY=$(openssl rand -hex 32)
export CRYPT_SECRET_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# Frontend
export VITE_API_URL=http://localhost:8000
```

## Production

All secrets must be provided via environment variables or a secrets manager. Never commit `.env` files.
