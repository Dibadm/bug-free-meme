# Security Flow

## Authentication

1. Telegram init data validation (HMAC-SHA256)
2. JWT access token creation
3. Session creation with token hash
4. Session validation on each request

## Authorization

- Role-based access control (PLAYER, MODERATOR, ADMIN, SUPER_ADMIN)
- Permission checks in services and endpoints
- Admin-only endpoints protected by role check

## WebSocket Security

- JWT token passed as query parameter
- Session validation on connect
- User status check (banned, deleted)
- Rate limiting per connection
- Replay attack prevention via nonce
- CSRF protection for state-changing HTTP requests
- Security headers (HSTS, X-Frame-Options, CSP)

## Audit Logging

- All sensitive actions logged with actor, action, entity, IP, user agent
- Admin actions tracked separately
- Audit logs archived daily

## Data Protection

- Passwords hashed with bcrypt
- API keys hashed with SHA-256
- Secrets stored in environment variables
- No secrets in code or logs
