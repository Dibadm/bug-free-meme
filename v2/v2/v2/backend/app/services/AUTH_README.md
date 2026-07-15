# Phase 3: Authentication & User Lifecycle

## Authentication Architecture

### Telegram Mini App Authentication

The backend validates Telegram Web App `initData` using HMAC-SHA256 signature verification following Telegram's official recommendations.

**Flow:**
1. Client sends `initData` string from Telegram Web App
2. Backend parses key-value pairs from `initData`
3. Extracts `hash` field
4. Computes expected HMAC using `TELEGRAM_SECRET_TOKEN`
5. Compares signatures using constant-time comparison
6. Validates `auth_date` is within 24 hours (replay protection)
7. Extracts user profile from validated data

**Security Features:**
- Signature verification prevents tampering
- Timestamp validation prevents replay attacks
- Constant-time comparison prevents timing attacks
- 24-hour window limits replay window

### Session Management

Sessions are stored in the `sessions` table with:
- `token_hash` - SHA256 hash of JWT (indexed, unique)
- `expires_at` - session expiration timestamp
- `revoked_at` - soft revocation timestamp
- `device_info`, `ip_address`, `user_agent` - audit metadata
- `last_used_at` - for session cleanup

**Lifecycle:**
1. User authenticates → JWT created + session record created
2. Subsequent requests → token validated against active sessions
3. Logout → session revoked
4. Logout all → all user sessions revoked
5. Expired sessions → cleaned up periodically

### First Login Atomic Initialization

When a user authenticates for the first time, the following are created atomically:
1. `User` record with telegram profile data
2. `Wallet` with zero balances
3. `PlayerStatistics` with zero counters
4. `UserProfile` with default settings
5. `NotificationPreference` records (game, wallet, announcement, admin)
6. `Leaderboard` entry for global ranking
7. Audit log entry for registration

All operations execute within a single database transaction.

### Returning User Synchronization

On each login:
- Username, first_name, last_name synchronized from Telegram
- Language preference updated
- `last_seen` and `last_login` timestamps updated
- Audit log entry created

## Session Architecture

### Token Structure

JWT access tokens contain:
- `sub` - user UUID
- `telegram_id` - Telegram user ID
- `role` - user role (player, moderator, admin, super_admin)
- `exp` - expiration timestamp
- `iat` - issued at timestamp

### Session Storage

| Field | Type | Purpose |
|-------|------|---------|
| `id` | UUID | Primary key |
| `user_id` | UUID | Owner |
| `token_hash` | VARCHAR(255) | SHA256 of JWT |
| `device_info` | VARCHAR(255) | Device description |
| `ip_address` | VARCHAR(45) | IPv4/IPv6 |
| `user_agent` | VARCHAR(500) | Browser/device |
| `expires_at` | TIMESTAMP | Session expiry |
| `last_used_at` | TIMESTAMP | Last activity |
| `revoked_at` | TIMESTAMP | Revocation time |

### Multi-Device Support

Users can have multiple active sessions simultaneously. Each login creates a new session. Sessions can be individually revoked.

## Permission Model

### Role Hierarchy

| Role | Level | Permissions |
|------|-------|-------------|
| PLAYER | 0 | Default user permissions |
| MODERATOR | 1 | Player + moderation |
| ADMIN | 2 | Player + moderation + admin |
| SUPER_ADMIN | 3 | Full access |

### Permission Checking

```python
from app.core.permissions import PermissionMiddleware

# In route or dependency
checker = PermissionMiddleware.require_role(UserRole.ADMIN)
user = await checker(user)
```

Roles are checked hierarchically - higher roles inherit lower role permissions.

## User Lifecycle

```
ANONYMOUS
    ↓ (authenticate via Telegram)
AUTHENTICATED
    ↓ (first login completes)
REGISTERED
    ↓ (admin verification)
VERIFIED
    ↓ (active gameplay)
ACTIVE
    ↓ (admin action)
SUSPENDED
    ↓ (admin action)
BANNED
    ↓ (soft delete)
DELETED
```

Every transition generates an audit log entry.

## Telegram Authentication Process

1. **Client-side**: Telegram Web App provides `initData` string
2. **Server-side**:
   - Parse `init_data` into key-value pairs
   - Extract and remove `hash` field
   - Create `data_check_string` by sorting and joining pairs
   - Compute HMAC-SHA256 using `TELEGRAM_SECRET_TOKEN`
   - Compare with received `hash`
   - Validate `auth_date` is within 24 hours
3. **On success**:
   - Extract user profile from validated data
   - Create or update user record
   - Create session
   - Return JWT

## Security Decisions

1. **JWT over opaque tokens**: Stateless, scalable, standard
2. **SHA256(token) storage**: Allows session validation without storing plaintext tokens
3. **24-hour initData window**: Balances security and usability
4. **Role-based access**: Centralized permission checks
5. **Audit logging**: All authentication events logged
6. **Soft delete**: User data preserved for audit/compliance
7. **Atomic first-login**: All-or-nothing user initialization

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | /auth/login | Authenticate with Telegram initData |
| POST | /auth/logout | Revoke current session |
| POST | /auth/refresh | Refresh authentication |
| GET | /auth/me | Get current user profile |
| PATCH | /profile | Update profile settings |
| GET | /sessions | List active sessions |
| DELETE | /sessions/{id} | Revoke specific session |
| POST | /referrals/apply | Apply referral code |

## Out of Scope

- Telegram Bot commands
- Admin interface
- Wallet UI
- Game UI
- Payment integration
