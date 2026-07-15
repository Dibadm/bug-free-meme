# Notification Events

## Types

| Type | Description |
|------|-------------|
| winner | Winner notification |
| deposit_approved | Deposit approved |
| withdrawal_approved | Withdrawal approved |
| maintenance_alert | Maintenance alert |
| announcement | General announcement |
| daily_reward_reminder | Daily reward reminder |
| referral_reward | Referral reward notification |
| game_started | Game started |
| game_ended | Game ended |
| system | System notification |

## Priorities

- high
- normal
- silent

## Status

- pending
- scheduled
- sent
- failed
- read

## Delivery

- Real-time via WebSocket
- Queued via background worker
- Telegram push notification
- Retry queue on failure

## Preferences

Users can enable/disable per notification type.
