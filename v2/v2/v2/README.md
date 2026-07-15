# Habesha Bet V2

Premium Telegram Mini App Gaming Platform.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, Vite, TypeScript, Tailwind CSS, Framer Motion |
| Backend | FastAPI, Python 3.12, SQLAlchemy 2, Alembic |
| Engine | Standalone Python package (framework-agnostic) |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Infra | Docker, Docker Compose, Nginx |

## Structure

```
v2/
├── backend/          FastAPI backend
│   ├── app/
│   │   ├── api/v1/   API routes
│   │   ├── core/     Config, security, logging
│   │   ├── models/   SQLAlchemy models
│   │   ├── schemas/  Pydantic schemas
│   │   ├── services/ Business logic
│   │   └── adapters/ External integrations
│   ├── tests/        Backend tests
│   └── alembic/      Database migrations
├── engine/           Standalone game engine
│   ├── src/          Engine code
│   └── tests/        Engine tests
├── frontend/         React + Vite app
│   ├── src/
│   │   ├── components/ Design system
│   │   ├── pages/     Route pages
│   │   ├── hooks/     Custom hooks
│   │   ├── lib/       Utilities, providers
│   │   └── styles/    Global styles
│   └── public/       Static assets
├── infra/            Nginx config
├── shared/           Cross-cutting types
└── .github/workflows CI/CD
```

## Getting Started

```bash
# 1. Clone and install
git clone <repo>
cd habesha-bet-v2
cp .env.example .env

# 2. Start infrastructure
docker compose up -d db redis

# 3. Backend
cd backend
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload

# 4. Frontend
cd frontend
npm install
npm run dev
```

## Scripts

```bash
# Backend
cd backend
ruff check .              # Lint
mypy app/                 # Typecheck
pytest tests/ -v          # Tests
alembic upgrade head      # Migrate DB

# Engine
cd engine
pytest tests/ -v          # Tests

# Frontend
cd frontend
npm run lint              # Lint
npm run typecheck         # Typecheck
npm run build             # Build

# All
pre-commit run --all-files
```

## Documentation

- `CONTRIBUTING.md` - Contribution guidelines
- `ENV.md` - Environment variables
- `ARCHITECTURE.md` - System architecture
- `CODING_STANDARDS.md` - Code style guide

## License

Proprietary
