# CONTRIBUTING

Thank you for contributing to Habesha Bet V2.

## Prerequisites

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL 16+
- Redis 7+

## Setup

```bash
git clone <repository-url>
cd habesha-bet-v2
cp .env.example .env
# Edit .env with your values

# Start infrastructure
docker compose up -d db redis

# Backend
cd backend
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Engine tests
cd engine
pip install -e ".[dev]"
pytest tests/ -v
```

## Code Quality

```bash
# Pre-commit hooks (recommended)
pip install pre-commit
pre-commit install

# Backend
cd backend
ruff check .
mypy app/
pytest tests/ -v

# Frontend
cd frontend
npm run lint
npm run typecheck
```

## Branching

- `main` - Production
- `develop` - Integration branch
- `feature/*` - New features
- `fix/*` - Bug fixes

## Commit Messages

Follow conventional commits:

- `feat: add user search`
- `fix: handle null wallet`
- `docs: update architecture`
- `chore: bump dependencies`
