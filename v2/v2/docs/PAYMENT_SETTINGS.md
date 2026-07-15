# Payment Settings

## Overview

The Telebirr deposit system is fully configurable via the admin panel. No code changes are required when changing the Telebirr number or account details.

## Admin Configuration

Admins can configure:

- Telebirr phone number
- Account holder name
- Deposit instructions
- Minimum deposit amount
- Maximum deposit amount
- Deposit enabled/disabled toggle
- Auto-credit enabled/disabled toggle
- Maintenance message

Access via: `/admin/payment-settings` (GET/PATCH)

## Player Flow

1. Player opens Wallet page
2. Player taps Deposit
3. Player sees current Telebirr number, account name, and instructions
4. Player sends money to the Telebirr number
5. Player receives SMS confirmation
6. Player pastes SMS into the app
7. Backend verifies SMS contains the configured Telebirr number
8. If auto-credit is enabled, wallet is credited automatically
9. If auto-credit is disabled, deposit waits for admin approval

## SMS Verification

- Backend verifies the SMS contains the currently configured Telebirr number
- Rejects SMS for old numbers after admin changes the number
- Prevents duplicate SMS usage per deposit
- Prevents replay attacks via timestamp validation

## Public API

`GET /payment-settings` returns only public information:

- Telebirr number
- Account holder name
- Deposit instructions
- Minimum/maximum deposit
- Whether deposits are enabled
- Maintenance message

## Audit Log

Every payment settings change is logged with:

- Admin user ID
- Old values
- New values
- Timestamp
- IP address
- User agent

## Live Updates

When an admin updates payment settings, all connected clients receive a WebSocket event:

```json
{
  "event": "payment.settings.updated",
  "data": {
    "settings": { ... }
  }
}
```

Clients update their UI immediately without requiring a page refresh.
