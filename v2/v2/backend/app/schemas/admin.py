from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas import BaseSchema


class AdminUserSearch(BaseSchema):
    id: UUID
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    wallet_balance: Decimal
    status: str

    model_config = ConfigDict(from_attributes=True)


class WalletAdjustment(BaseSchema):
    user_id: UUID
    amount: Decimal
    reason: str


class SearchUsersQuery(BaseSchema):
    query: str
    page: int = 1
    page_size: int = 20


class AdminActionRead(BaseSchema):
    id: UUID
    admin_id: UUID
    action: str
    target_type: str | None = None
    target_id: UUID | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogRead(BaseSchema):
    id: UUID
    actor_id: UUID | None = None
    action: str
    entity_type: str | None = None
    entity_id: UUID | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DailyRewardRead(BaseSchema):
    id: UUID
    day: int
    amount: Decimal
    claimed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AchievementRead(BaseSchema):
    id: UUID
    name: str
    description: str
    type: str
    threshold: int
    reward_amount: Decimal | None = None
    icon: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PaymentSettingsRead(BaseSchema):
    id: UUID
    telebirr_number: str
    account_holder_name: str
    deposit_instructions: str
    min_deposit: Decimal
    max_deposit: Decimal
    is_deposit_enabled: bool
    auto_credit_enabled: bool
    maintenance_message: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentSettingsUpdate(BaseSchema):
    telebirr_number: str | None = None
    account_holder_name: str | None = None
    deposit_instructions: str | None = None
    min_deposit: Decimal | None = None
    max_deposit: Decimal | None = None
    is_deposit_enabled: bool | None = None
    auto_credit_enabled: bool | None = None
    maintenance_message: str | None = None
    is_active: bool | None = None
