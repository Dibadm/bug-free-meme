# Session Fixes — 2026-07-15

## Environment
- **Workspace:** `C:\Users\hp\Desktop\v2\`
- **DB:** PostgreSQL 16 on localhost:5432, database `habesha_bet`, user `habesha`
- **Python:** 3.13 (path: `C:\Users\hp\AppData\Local\Programs\Python\Python313\python.exe`)

---

## Issues Fixed

### 1. RateLimitMiddleware parameter mismatch
- **Files:** `backend\app\main.py`, `v2\v2\backend\app\main.py`
- **Line:** 78
- **Fix:** Changed `requests_per_minute=...` to `rate_limit=...` to match `RateLimitMiddleware.__init__(app, rate_limit, window)` in `app\core\middleware.py`

### 2. Missing database migrations — tables did not exist
- **Symptom:** `UndefinedTableError: relation "notifications" does not exist`
- **Root cause:** Alembic migrations had never been applied to the local database
- **Fix:**
  - Updated `backend\alembic\env.py` to handle missing `alembic.ini` and removed invalid `sqlalchemy.future` setting
  - Fixed migration `003_auth_lifecycle.py` to explicitly `CREATE TYPE userrole AS ENUM (...)` before adding the column (asyncpg doesn't handle `sa.Enum(...)` in `add_column` well)
  - Ran `alembic upgrade head` — all 30+ tables created

### 3. `WalletTransactionStatus` NameError
- **Files:** `v2\v2\backend\app\models\models.py`
- **Fix:** Added `WalletTransactionStatus = TransactionStatus` alias after `TransactionStatus` enum definition

### 4. `RoomStatus.ACTIVE` used but not defined
- **Files:** `v2\v2\backend\app\models\models.py`
- **Fix:** Changed `RoomStatus.ACTIVE` to `RoomStatus.DRAFT` (the correct default for room templates)

### 5. Missing `schedule_pending_rooms` method on RoomService
- **Files:** `backend\app\services\room_service.py`, `v2\v2\backend\app\services\room_service.py`
- **Fix:** Added stub method `async def schedule_pending_rooms(self) -> None: pass`

### 6. Bot runner — `KeyError: 0` on `set_my_commands`
- **Files:** `backend\app\bot\runner.py`, `v2\v2\backend\app\bot\runner.py`
- **Fix:** `telegram_bot.get_commands()` returns `list[dict[str, str]]` but `set_my_commands()` expects `BotCommand` objects. Changed to:
  ```python
  commands = [BotCommand(cmd["command"], cmd["description"]) for cmd in telegram_bot.get_commands()]
  ```
  Also added `BotCommand` to the `telegram` import.

### 7. Notification columns missing from DB schema
- **Symptom:** `UndefinedColumnError: column notifications.read_at does not exist`
- **Root cause:** `001_initial_schema` created `notifications` with only basic columns, but the model and queries expect `read_at`, `status`, `priority`, `scheduled_at`, `sent_at`, `retry_count`
- **Fix:** Created migration `backend\alembic\versions\005_notification_fields.py` adding all missing columns

### 8. NotificationStatus enum mismatch (uppercase vs lowercase)
- **Symptom:** `InvalidTextRepresentationError: invalid input value for enum notificationstatus: "PENDING"`
- **Root cause:** SQLAlchemy asyncpg sends enum *member names* (`PENDING`, `FAILED`), but the enum was created with lowercase *values* (`pending`, `failed`)
- **Fix:**
  - Changed `NotificationStatus` enum values to uppercase: `PENDING = "PENDING"`, `FAILED = "FAILED"`, etc.
  - Updated `notification_repository.py` line 63: `"sent"` → `"SENT"`
  - Updated `background_workers.py` line 313: `"pending"` → `"PENDING"`
  - Updated `tests\services\test_notification.py` lines 37-38
  - Updated migration `005_notification_fields.py` to create enum with uppercase values
  - Dropped old enum type and re-ran `alembic upgrade head`

### 9. Missing `DailyRewardService` import in ReminderWorker
- **Symptom:** `cannot import name 'DailyRewardService' from 'app.services'`
- **Fix:** Removed the missing service import and call from `background_workers.py` `ReminderWorker._send_reminders()` in both `backend` and `v2\v2\backend` copies

---

## Paused / Not Yet Implemented
- `DailyRewardService` — referenced in old code but never created. The model (`DailyReward`) and repository (`DailyRewardRepository`) exist, but the service class is missing. If you need daily reward functionality, you'll need to implement it.

---

## Duplicate Codebase Warning
Two copies of the backend exist:
- **Primary (used by uvicorn):** `C:\Users\hp\Desktop\v2\backend\`
- **Duplicate:** `C:\Users\hp\Desktop\v2\v2\backend\`

Most fixes were applied to **both** copies to keep them in sync, but going forward, only the `backend\` copy is actively used. Consider consolidating or deleting the `v2\v2\` copy.

---

## How to resume on home PC
1. Ensure PostgreSQL is running and database `habesha_bet` exists
2. Copy `.env` file (it has your config but no secrets beyond DB creds)
3. Install deps: `pip install -e ".[dev]"`
4. Run migrations: `alembic upgrade head`
5. Start backend: `py -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
6. Start bot (new terminal): `py -m app.bot.runner`
