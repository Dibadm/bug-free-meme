# Recovery Flow

## Game Recovery

- Engine records game state to database after each ball call
- If server crashes, game state is recoverable from `games` and `called_numbers` tables
- Game status set to `RECOVERED` after restoration
- Clients reconnect and sync state via WebSocket

## Session Recovery

- Sessions stored with expiry timestamps
- Expired sessions cleaned up by CleanupWorker
- Users can refresh tokens via `/auth/refresh`

## WebSocket Recovery

- Clients maintain local game state
- On reconnect, client requests current game state
- Server broadcasts missed events since last known state
- Exponential backoff for reconnection

## Database Recovery

- PostgreSQL with WAL archiving
- Point-in-time recovery supported
- Alembic migrations for schema changes

## Notification Recovery

- Failed notifications stored with retry count
- RetryQueueWorker retries failed notifications
- Max retry limit prevents infinite loops
