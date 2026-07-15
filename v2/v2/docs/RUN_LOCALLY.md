# Habesha Bet V2 - Local Development Setup

## Step 1 - Prerequisites

Install the following before continuing:

- **Python 3.12+** — https://python.org
- **Node.js 18+** (LTS recommended) — https://nodejs.org
- **PostgreSQL 16** — https://postgresql.org/download/
- **Redis 7** — https://redis.io/download
- **Git** — https://git-scm.com

> **Note:** If you have Docker Desktop, you can skip PostgreSQL/Redis manual install and use `docker compose up -d db redis` instead.

---

## Step 2 - Clone and Install

```bash
git clone <your-repo-url>
cd v2
```

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
pip install -e ".[dev]"
```

### Frontend
```bash
cd frontend
npm install
```

---

## Step 3 - Environment Variables

Create `.env` in the project root (same level as `docker-compose.yml`).

### Required Variables

| Variable | Required | Where to Obtain |
|----------|----------|-----------------|
| `TELEGRAM_BOT_TOKEN` | **YES** | Message @BotFather on Telegram, send `/newbot`, copy token |
| `TELEGRAM_WEB_APP_URL` | **YES** | Your public HTTPS URL where frontend is hosted. For local testing: `https://<your-tunnel>.ngrok-free.app` |
| `TELEGRAM_SECRET_TOKEN` | **YES** | Any random string (e.g., `openssl rand -hex 32`). Used to validate Telegram webhook calls |
| `JWT_SECRET_KEY` | **YES** | Any long random string (e.g., `openssl rand -hex 32`). Used to sign JWT tokens |
| `HOUSE_WALLET_ID` | **YES** | UUID of the house wallet. Create one via admin panel or database seed |
| `ADMIN_IDS` | **YES** | Comma-separated Telegram user IDs of admins. Get your Telegram ID from @userinfobot |
| `CRYPT_SECRET_KEY` | **YES** | 32-byte base64 string for Fernet encryption (e.g., `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`) |
| `DATABASE_URL` | Auto | Default: `postgresql+asyncpg://habesha:habesha_secret@localhost:5432/habesha_bet` |
| `REDIS_URL` | Auto | Default: `redis://localhost:6379/0` |
| `GAME_ENGINE_HOST` | Auto | Default: `localhost` |
| `GAME_ENGINE_PORT` | Auto | Default: `8001` |
| `VITE_API_URL` | Auto | Default: `http://localhost:8000` |
| `VITE_WS_URL` | Auto | Default: `ws://localhost:8000` |

### Example `.env`

```env
DEBUG=True
DATABASE_URL=postgresql+asyncpg://habesha:habesha_secret@localhost:5432/habesha_bet
REDIS_URL=redis://localhost:6379/0
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_WEB_APP_URL=https://your-app.ngrok-free.app
TELEGRAM_SECRET_TOKEN=your-secret-token-here
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080
HOUSE_WALLET_ID=00000000-0000-0000-0000-000000000000
ADMIN_IDS=123456789,987654321
CRYPT_SECRET_KEY=your-fernet-key-here
GAME_ENGINE_HOST=localhost
GAME_ENGINE_PORT=8001
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

---

## Step 4 - Database Setup

### Option A: Docker (easiest)
```bash
docker compose up -d db redis
```

### Option B: Manual install

1. Create database:
```sql
createdb habesha_bet
psql -U habesha -d habesha_bet -c "ALTER USER habesha WITH PASSWORD 'habesha_secret';"
```

2. Run migrations:
```bash
cd backend
venv\Scripts\activate
alembic upgrade head
```

---

## Step 5 - Start Services

Open **separate terminals** for each service:

### Terminal 1 - PostgreSQL
```bash
# If using Docker:
docker compose up db

# If manual:
pg_ctl -D "C:\Program Files\PostgreSQL\16\data" start
# Or start PostgreSQL service from Windows Services
```

### Terminal 2 - Redis
```bash
# If using Docker:
docker compose up redis

# If manual:
redis-server
```

### Terminal 3 - Backend API
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 4 - Frontend
```bash
cd frontend
npm run dev
```

### Terminal 5 - Telegram Bot
```bash
cd backend
venv\Scripts\activate
python -m app.bot.runner
```

---

## Step 6 - Verify

| Service | URL | Expected |
|---------|-----|----------|
| Backend API | http://localhost:8000/health | `{"status":"ok"}` |
| Backend Docs | http://localhost:8000/docs | Swagger UI |
| Frontend | http://localhost:5173 | Habesha Bet home page |
| WebSocket | `ws://localhost:8000/api/v1/ws?token=...` | Connection established |
| Telegram Bot | Message @your_bot `/start` | Bot replies with Mini App button |

---

## Telegram Bot Configuration Details

| Setting | Location | Value |
|---------|----------|-------|
| Token | `TELEGRAM_BOT_TOKEN` in `.env` | From @BotFather |
| Web App URL | `TELEGRAM_WEB_APP_URL` in `.env` | Your public HTTPS URL |
| Secret Token | `TELEGRAM_SECRET_TOKEN` in `.env` | Random string for webhook validation |
| Mini App | Set via BotFather: `/mybots` → *Your Bot* → **Bot Settings** → **Menu Button** → **Configure Menu Button** | Set to your Web App URL |

### How to connect your own Telegram bot:

1. Open Telegram, message **@BotFather**
2. Send `/newbot`
3. Follow prompts to set bot name and username
4. Copy the token (format: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)
5. Paste into `.env` as `TELEGRAM_BOT_TOKEN`
6. Set `TELEGRAM_WEB_APP_URL` to your public HTTPS URL
7. Set `TELEGRAM_SECRET_TOKEN` to any random string
8. Start the bot with `python -m app.bot.runner`

---

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│              Telegram Client                 │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│              Nginx (80/443)                  │
│  /api/ → Backend  │  / → Frontend           │
└──────────┬──────────────────────┬────────────┘
           │                      │
           ▼                      ▼
┌──────────────────┐   ┌──────────────────┐
│   Backend        │   │   Frontend       │
│   FastAPI        │   │   React + TS     │
│   Port 8000      │   │   Port 5173      │
│                  │   │                  │
│  - REST API      │   │  - Pages         │
│  - WebSocket     │   │  - Components    │
│  - Bot Runner    │   │  - Hooks         │
│  - Workers       │   │  - Telegram SDK  │
└────────┬─────────┘   └──────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────┐
│Postgres│ │ Redis │
│ 5432  │ │ 6379  │
└───────┘ └───────┘
```

### How services work together:

1. **Frontend** (React) serves the Telegram Mini App at `http://localhost:5173`
2. **Backend** (FastAPI) provides:
   - REST API at `http://localhost:8000/api/v1`
   - WebSocket at `ws://localhost:8000/api/v1/ws`
   - Background workers for notifications, reminders, cleanup
3. **Telegram Bot** connects to Telegram via polling/webhook
4. **PostgreSQL** stores all persistent data
5. **Redis** is used for caching and session storage
6. **Nginx** (production only) reverse-proxies frontend and backend

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `TELEGRAM_BOT_TOKEN is not set` | Fill in `.env` with token from @BotFather |
| `Database connection refused` | Start PostgreSQL: `docker compose up db` or `pg_ctl start` |
| `Redis connection refused` | Start Redis: `docker compose up redis` or `redis-server` |
| `ModuleNotFoundError` | Run `pip install -e ".[dev]"` in backend directory |
| `Port 8000 already in use` | Kill process or use `--port 8001` |
| `Port 5173 already in use` | Kill process or use `npm run dev -- --port 3000` |
| Frontend can't reach backend | Set `VITE_API_URL=http://localhost:8000` in `.env` |
| Telegram bot not responding | Check token, ensure bot is not running elsewhere |

---

## Next Steps After Setup

1. Create an admin user via Django admin or database seed
2. Configure payment settings at `/admin/payment-settings`
3. Test deposit flow with SMS verification
4. Test game creation and bingo gameplay
5. Test withdrawal flow
