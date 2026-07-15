from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas import BaseSchema


class WalletTransactionCreate(BaseSchema):
    type: str
    amount: Decimal
    reference_id: str | None = None
    description: str | None = None
    metadata: dict | None = None


class DepositCreate(BaseSchema):
    amount: Decimal
    proof_url: str | None = None
    sms_code: str | None = None


class DepositRead(BaseSchema):
    id: UUID
    user_id: UUID
    amount: Decimal
    status: str
    proof_url: str | None = None
    sms_code: str | None = None
    sms_sent_to: str | None = None
    sms_verified_at: datetime | None = None
    reviewed_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SMSVerifyRequest(BaseSchema):
    deposit_id: UUID
    sms_text: str


class WithdrawalCreate(BaseSchema):
    amount: Decimal
    phone_number: str


class WithdrawalRead(BaseSchema):
    id: UUID
    user_id: UUID
    amount: Decimal
    phone_number: str
    status: str
    rejection_reason: str | None = None
    reviewed_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransferCreate(BaseSchema):
    to_user_id: UUID
    amount: Decimal


class PlayerStatsRead(BaseSchema):
    games_played: int
    games_won: int
    win_rate: Decimal
    current_streak: int
    best_streak: int
    cards_purchased: int
    total_deposited: Decimal
    total_withdrawn: Decimal
    total_won: Decimal
    referral_earnings: Decimal

    model_config = ConfigDict(from_attributes=True)


class ReferralRead(BaseSchema):
    id: UUID
    referrer_username: str | None = None
    referred_username: str | None = None
    total_earned: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnnouncementRead(BaseSchema):
    id: UUID
    title: str
    body: str
    is_active: bool
    priority: int
    published_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationRead(BaseSchema):
    id: UUID
    title: str
    body: str
    type: str
    is_read: bool
    data: dict | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminDashboard(BaseSchema):
    revenue_today: Decimal
    revenue_month: Decimal
    active_players: int
    active_games: int
    pending_withdrawals: int
    house_balance: Decimal
    total_deposits_pending: Decimal


class EmergencyControls(BaseSchema):
    maintenance_mode: bool
    message: str | None = None


class PublicPaymentSettings(BaseSchema):
    telebirr_number: str
    account_holder_name: str
    deposit_instructions: str
    min_deposit: Decimal
    max_deposit: Decimal
    is_deposit_enabled: bool
    maintenance_message: str | None = None
