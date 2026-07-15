# Authentication Flow

## Telegram Mini App

1. User opens Mini App via Telegram
2. Telegram provides `initData` to frontend
3. Frontend sends `initData` to `/api/v1/auth/validate`
4. Backend validates HMAC-SHA256 signature
5. Backend creates/updates user record
6. Backend creates JWT access token
7. Backend creates session record with token hash
8. Frontend stores token and uses it for subsequent requests

## WebSocket

1. Frontend connects to `/api/v1/ws?token=<JWT>`
2. Backend extracts token from query
3. Backend validates session and token
4. Backend checks user status
5. Connection established and subscribed to default channels

## Session Management

- Sessions stored in database with token hash
- Sessions expire after configured TTL
- Sessions can be revoked on logout
- Multiple sessions per user supported

## Token Refresh

- Access tokens are long-lived (7 days default)
- Refresh via `/api/v1/auth/refresh` with new initData
- Old sessions remain valid until expiry or revocation
