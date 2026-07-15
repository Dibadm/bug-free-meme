# Repositories

Data access layer.

## Purpose

Provides a clean abstraction over database operations.

## Base Repository

`BaseRepository` provides common CRUD operations:
- `get_by_id`
- `get_all`
- `find_one`
- `find_many`
- `create`
- `update`
- `delete`
- `soft_delete`
- `exists`
- `count`

## Repositories

| Repository | Aggregate | Purpose |
|-----------|----------|---------|
| `UserRepository` | User | Telegram user lookup, admin users |
| `WalletRepository` | Wallet | Balance queries |
| `WalletTransactionRepository` | WalletTransaction | Transaction history by type |
| `RoomTemplateRepository` | RoomTemplate | Active templates, pattern lookup |
| `RoomRepository` | Room | Room lifecycle, card/player counts |
| `GameRepository` | Game | Active/finished games by room |
| `CardRepository` | Card | Available cards, sold counts |
| `PurchasedCardRepository` | PurchasedCard | User cards, winners |
| `CalledNumberRepository` | CalledNumber | Game call history |
| `DepositRepository` | Deposit | Pending deposits, user history |
| `WithdrawalRepository` | Withdrawal | Pending withdrawals, user history |
| `PrizePayoutRepository` | PrizePayout | Prize history by game/user |
| `AnnouncementRepository` | Announcement | Active announcements |
| `NotificationRepository` | Notification | User notifications, unread counts |
| `ReferralRepository` | ReferralAccount | Referrer/referred accounts |
| `ReferralRewardRepository` | ReferralReward | Reward history |
| `AchievementRepository` | Achievement | Active achievements, by type |
| `AchievementProgressRepository` | AchievementProgress | User progress, completed |
| `StatisticsRepository` | PlayerStatistics | User stats, top players |
| `AuditRepository` | AuditLog | Actor logs, entity logs, recent |
| `LeaderboardRepository` | Leaderboard | Period rankings, user rank |
| `SettingsRepository` | Setting | Key lookup, public settings |
| `FeatureFlagRepository` | FeatureFlag | Enabled flags |
| `MaintenanceModeRepository` | MaintenanceMode | Current mode |
| `AdminActionRepository` | AdminAction | Admin action history |
| `SystemLogRepository` | SystemLog | Logs by level |

## Conventions

- Repositories never raise HTTP exceptions
- Repositories never contain business rules
- Repositories return model instances or simple DTOs
- All queries are async
- Soft delete uses `deleted_at` column
