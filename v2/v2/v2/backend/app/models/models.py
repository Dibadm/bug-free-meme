from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserStatus(str, Enum):
    ANONYMOUS = "anonymous"
    AUTHENTICATED = "authenticated"
    REGISTERED = "registered"
    VERIFIED = "verified"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    DELETED = "deleted"


class UserRole(str, Enum):
    PLAYER = "player"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class WalletTransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    PURCHASE = "purchase"
    PRIZE = "prize"
    REFERRAL = "referral"
    BONUS = "bonus"
    JACKPOT = "jackpot"
    ADJUSTMENT = "adjustment"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"


WalletTransactionStatus = TransactionStatus


class GameStatus(str, Enum):
    WAITING = "waiting"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"
    CANCELLED = "cancelled"
    RECOVERED = "recovered"


class RoomStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    WAITING = "waiting"
    OPEN = "open"
    LOCKED = "locked"
    RUNNING = "running"
    FINISHED = "finished"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class VisibilityType(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    VIP = "vip"


class AchievementType(str, Enum):
    WIN_RATE = "win_rate"
    GAMES_PLAYED = "games_played"
    WIN_STREAK = "win_streak"
    REFERRAL_COUNT = "referral_count"
    TOTAL_WON = "total_won"


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="am")
    status: Mapped[UserStatus] = mapped_column(SQLEnum(UserStatus), default=UserStatus.ACTIVE)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.PLAYER)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    referral_code: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    wallet: Mapped["Wallet"] = relationship("Wallet", back_populates="user", uselist=False, cascade="all, delete-orphan")
    statistics: Mapped["PlayerStatistics"] = relationship("PlayerStatistics", back_populates="user", uselist=False, cascade="all, delete-orphan")
    referrals_sent: Mapped[list["ReferralAccount"]] = relationship("ReferralAccount", foreign_keys="ReferralAccount.referrer_id", back_populates="referrer", cascade="all, delete-orphan")
    referrals_received: Mapped[list["ReferralAccount"]] = relationship("ReferralAccount", foreign_keys="ReferralAccount.referred_id", back_populates="referred", cascade="all, delete-orphan")
    achievement_progress: Mapped[list["AchievementProgress"]] = relationship("AchievementProgress", back_populates="user", cascade="all, delete-orphan")
    daily_rewards: Mapped[list["DailyReward"]] = relationship("DailyReward", back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    deposits: Mapped[list["Deposit"]] = relationship("Deposit", back_populates="user", cascade="all, delete-orphan")
    withdrawals: Mapped[list["Withdrawal"]] = relationship("Withdrawal", back_populates="user", cascade="all, delete-orphan")
    admin_actions: Mapped[list["AdminAction"]] = relationship("AdminAction", back_populates="admin", cascade="all, delete-orphan")
    audit_logs: Mapped[list["AuditLog"]] = relationship("AuditLog", foreign_keys="AuditLog.actor_id", back_populates="actor", cascade="all, delete-orphan")
    sessions: Mapped[list["Session"]] = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    profile: Mapped["UserProfile"] = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    notification_preferences: Mapped[list["NotificationPreference"]] = relationship("NotificationPreference", back_populates="user", cascade="all, delete-orphan")


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    bonus_balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    jackpot_balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    total_deposited: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    total_withdrawn: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    total_won: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    total_spent: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship("User", back_populates="wallet")
    transactions: Mapped[list["WalletTransaction"]] = relationship("WalletTransaction", back_populates="wallet", cascade="all, delete-orphan")


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    wallet_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False)
    type: Mapped[WalletTransactionType] = mapped_column(SQLEnum(WalletTransactionType), nullable=False)
    status: Mapped[WalletTransactionStatus] = mapped_column(SQLEnum(WalletTransactionStatus), default=WalletTransactionStatus.PENDING)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    balance_before: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    balance_after: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    reference_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    approved_by: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    wallet: Mapped[Wallet] = relationship("Wallet", back_populates="transactions")


class RoomTemplate(Base):
    __tablename__ = "room_templates"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    entry_fee: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    max_cards_per_player: Mapped[int] = mapped_column(Integer, default=1)
    max_players: Mapped[int] = mapped_column(Integer, nullable=False)
    min_players: Mapped[int] = mapped_column(Integer, nullable=False)
    winning_pattern: Mapped[str] = mapped_column(String(100), nullable=False)
    ball_calling_speed: Mapped[int] = mapped_column(Integer, default=3)
    house_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    referral_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    bonus_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    jackpot_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    visibility: Mapped[VisibilityType] = mapped_column(SQLEnum(VisibilityType), default=VisibilityType.PUBLIC)
    status: Mapped[RoomStatus] = mapped_column(SQLEnum(RoomStatus), default=RoomStatus.DRAFT)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    rooms: Mapped[list["Room"]] = relationship("Room", back_populates="template", cascade="all, delete-orphan")


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    template_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("room_templates.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    game_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    status: Mapped[RoomStatus] = mapped_column(SQLEnum(RoomStatus), default=RoomStatus.DRAFT)
    current_players: Mapped[int] = mapped_column(Integer, default=0)
    cards_sold: Mapped[int] = mapped_column(Integer, default=0)
    prize_pool: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    template: Mapped[RoomTemplate] = relationship("RoomTemplate", back_populates="rooms")
    cards: Mapped[list["Card"]] = relationship("Card", back_populates="room", cascade="all, delete-orphan")


class Game(Base):
    __tablename__ = "games"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    room_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("rooms.id"), nullable=False, index=True)
    status: Mapped[GameStatus] = mapped_column(SQLEnum(GameStatus), default=GameStatus.WAITING, index=True)
    seed: Mapped[str | None] = mapped_column(String(255), nullable=True)
    seed_hash: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    called_numbers: Mapped[list[int] | None] = mapped_column(JSONB, nullable=True, default=list)
    current_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    winner_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    winning_pattern: Mapped[str | None] = mapped_column(String(100), nullable=True)
    prize_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    cards: Mapped[list["PurchasedCard"]] = relationship("PurchasedCard", back_populates="game", cascade="all, delete-orphan")
    called_numbers_records: Mapped[list["CalledNumber"]] = relationship("CalledNumber", back_populates="game", cascade="all, delete-orphan")
    winning_claims: Mapped[list["WinningClaim"]] = relationship("WinningClaim", back_populates="game", cascade="all, delete-orphan")


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    room_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("rooms.id"), nullable=False, index=True)
    numbers: Mapped[list[int]] = mapped_column(JSONB, nullable=False)
    pattern_index: Mapped[int] = mapped_column(Integer, nullable=False)
    is_sold: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    room: Mapped[Room] = relationship("Room", back_populates="cards")
    purchases: Mapped[list["PurchasedCard"]] = relationship("PurchasedCard", back_populates="card", cascade="all, delete-orphan")


class PurchasedCard(Base):
    __tablename__ = "purchased_cards"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    game_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("games.id"), nullable=False, index=True)
    card_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("cards.id"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    marks: Mapped[list[int] | None] = mapped_column(JSONB, nullable=True, default=list)
    is_winner: Mapped[bool] = mapped_column(Boolean, default=False)
    purchased_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    game: Mapped[Game] = relationship("Game", back_populates="cards")
    card: Mapped[Card] = relationship("Card", back_populates="purchases")


class CalledNumber(Base):
    __tablename__ = "called_numbers"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    game_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("games.id"), nullable=False, index=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    called_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    game: Mapped[Game] = relationship("Game", back_populates="called_numbers_records")


class WinningClaim(Base):
    __tablename__ = "winning_claims"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    game_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("games.id"), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    card_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("cards.id"), nullable=False)
    pattern: Mapped[str] = mapped_column(String(100), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    claimed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    game: Mapped[Game] = relationship("Game", back_populates="winning_claims")


class PrizePayout(Base):
    __tablename__ = "prize_payouts"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    game_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("games.id"), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    transaction_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("wallet_transactions.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    game: Mapped[Game] = relationship("Game")
    user: Mapped[User] = relationship("User")


class Deposit(Base):
    __tablename__ = "deposits"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    status: Mapped[TransactionStatus] = mapped_column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING)
    transaction_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("wallet_transactions.id"), nullable=True)
    proof_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sms_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    sms_sent_to: Mapped[str | None] = mapped_column(String(20), nullable=True)
    sms_verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reviewed_by: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship("User", back_populates="deposits")


class Withdrawal(Base):
    __tablename__ = "withdrawals"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[TransactionStatus] = mapped_column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING)
    transaction_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("wallet_transactions.id"), nullable=True)
    reviewed_by: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship("User", back_populates="withdrawals")


class Announcement(Base):
    __tablename__ = "announcements"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class NotificationStatus(str, Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    SENT = "sent"
    FAILED = "failed"
    READ = "read"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[NotificationStatus] = mapped_column(SQLEnum(NotificationStatus), default=NotificationStatus.PENDING)
    priority: Mapped[str] = mapped_column(String(20), default="normal")
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship("User", back_populates="notifications")


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[AchievementType] = mapped_column(SQLEnum(AchievementType), nullable=False)
    threshold: Mapped[int] = mapped_column(Integer, nullable=False)
    reward_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    progress: Mapped[list["AchievementProgress"]] = relationship("AchievementProgress", back_populates="achievement", cascade="all, delete-orphan")


class AchievementProgress(Base):
    __tablename__ = "achievement_progress"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    achievement_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("achievements.id"), nullable=False, index=True)
    current_value: Mapped[int] = mapped_column(Integer, default=0)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship("User", back_populates="achievement_progress")
    achievement: Mapped[Achievement] = relationship("Achievement", back_populates="progress")


class ReferralAccount(Base):
    __tablename__ = "referral_accounts"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    referrer_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    referred_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    reward_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    total_earned: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    referrer: Mapped[User] = relationship("User", foreign_keys=[referrer_id], back_populates="referrals_sent")
    referred: Mapped[User] = relationship("User", foreign_keys=[referred_id], back_populates="referrals_received")
    rewards: Mapped[list["ReferralReward"]] = relationship("ReferralReward", back_populates="referral", cascade="all, delete-orphan")


class ReferralReward(Base):
    __tablename__ = "referral_rewards"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    referral_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("referral_accounts.id"), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    transaction_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("wallet_transactions.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    referral: Mapped[ReferralAccount] = relationship("ReferralAccount", back_populates="rewards")


class DailyReward(Base):
    __tablename__ = "daily_rewards"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    day: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    claimed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship("User", back_populates="daily_rewards")


class PlayerStatistics(Base):
    __tablename__ = "player_statistics"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    games_played: Mapped[int] = mapped_column(Integer, default=0)
    games_won: Mapped[int] = mapped_column(Integer, default=0)
    win_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    best_streak: Mapped[int] = mapped_column(Integer, default=0)
    cards_purchased: Mapped[int] = mapped_column(Integer, default=0)
    total_deposited: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    total_withdrawn: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    total_won: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    referral_earnings: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship("User", back_populates="statistics")


class Leaderboard(Base):
    __tablename__ = "leaderboards"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    period: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    score: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship("User")


class AdminAction(Base):
    __tablename__ = "admin_actions"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    admin_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    target_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    target_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    admin: Mapped[User] = relationship("User", back_populates="admin_actions")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    actor_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    entity_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    old_value: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    new_value: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    actor: Mapped[User | None] = relationship("User", back_populates="audit_logs")


class Localization(Base):
    __tablename__ = "localizations"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    language_code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Setting(Base):
    __tablename__ = "settings"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class FeatureFlag(Base):
    __tablename__ = "feature_flags"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class MaintenanceMode(Base):
    __tablename__ = "maintenance_mode"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class PaymentSettings(Base):
    __tablename__ = "payment_settings"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    telebirr_number: Mapped[str] = mapped_column(String(20), nullable=False)
    account_holder_name: Mapped[str] = mapped_column(String(255), nullable=False)
    deposit_instructions: Mapped[str] = mapped_column(Text, nullable=False)
    min_deposit: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    max_deposit: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    is_deposit_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_credit_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    maintenance_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class SystemLog(Base):
    __tablename__ = "system_logs"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    level: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    device_info: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_used_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship("User", back_populates="sessions")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    privacy_settings: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship("User", back_populates="profile")


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    notification_type: Mapped[str] = mapped_column(String(50), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship("User", back_populates="notification_preferences")
