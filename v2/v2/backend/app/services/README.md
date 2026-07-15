# Services

Business logic layer.

## Purpose

Encapsulates all business rules and orchestration.

## Base Service

`BaseService` provides the database session to all services.

## Services

| Service | Aggregate | Responsibilities |
|---------|----------|-----------------|
| `UserService` | User | Create/update/ban users, Telegram auth |
| `WalletService` | Wallet | Credit, debit, balance queries |
| `TransferService` | Wallet | Atomic transfers between users |
| `DepositService` | Deposit | Create, approve, reject deposits |
| `WithdrawalService` | Withdrawal | Create, approve, reject withdrawals |
| `RoomTemplateService` | RoomTemplate | Create/activate templates, validate config |
| `RoomService` | Room | Room lifecycle, start/finish games |
| `GameService` | Game | Pause/resume/cancel/finish games |
| `CardService` | Card | Generate cards, availability queries |
| `PurchaseService` | PurchasedCard | Purchase cards, mark numbers |
| `AnnouncementService` | Announcement | Publish/deactivate announcements |
| `NotificationService` | Notification | Create, read, unread counts |
| `ReferralService` | ReferralAccount | Create referrals, query accounts |
| `AchievementService` | Achievement | Create achievements, update progress |
| `StatisticsService` | PlayerStatistics | Record games, deposits, wins |
| `LeaderboardService` | Leaderboard | Update scores, rankings |
| `AuditService` | AuditLog | Log all important actions |
| `AdminService` | Mixed | Search users, adjust wallets, maintenance |
| `SettingsService` | Setting | Key-value settings, feature flags |
| `LocalizationService` | Localization | Translation CRUD |

## Transaction Management

Financial operations use atomic database transactions:
- Deposit approval credits wallet atomically
- Withdrawal creation debits wallet atomically
- Transfers debit and credit atomically
- Prize distribution credits atomically

## Validation

Business validation lives in services:
- Cannot create duplicate deposits
- Cannot approve already approved withdrawals
- Cannot purchase sold cards
- Cannot start game in wrong room state
- Room template percentages must not exceed 100%

## Error Handling

Services raise domain exceptions:
- `ValidationError` - Business rule violation
- `InsufficientBalanceError` - Not enough funds
- `RoomClosedError` - Room not accepting joins
- `DuplicateCardError` - Card already purchased
- `InvalidWithdrawalError` - Invalid withdrawal state
- `InvalidDepositError` - Invalid deposit state
- `InvalidGameStateError` - Game in wrong state

## Conventions

- Services are stateless
- Services receive dependencies via constructor
- Services never import FastAPI
- Services never return HTTP responses
- All methods are async when accessing the database
