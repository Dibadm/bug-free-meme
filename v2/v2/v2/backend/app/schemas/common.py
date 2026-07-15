from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas import BaseSchema


class UserBase(BaseSchema):
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    language: str = "am"


class UserCreate(UserBase):
    pass


class UserUpdate(BaseSchema):
    phone_number: str | None = None
    language: str | None = None


class UserRead(UserBase):
    id: UUID
    is_admin: bool
    is_verified: bool
    last_seen: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WalletBase(BaseSchema):
    balance: Decimal = Field(default=Decimal("0.00"))
    bonus_balance: Decimal = Field(default=Decimal("0.00"))
    jackpot_balance: Decimal = Field(default=Decimal("0.00"))


class WalletRead(WalletBase):
    id: UUID
    user_id: UUID
    total_deposited: Decimal
    total_withdrawn: Decimal
    total_won: Decimal
    total_spent: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WalletTransactionBase(BaseSchema):
    type: str
    amount: Decimal


class WalletTransactionRead(WalletTransactionBase):
    id: UUID
    wallet_id: UUID
    status: str
    balance_before: Decimal
    balance_after: Decimal
    reference_id: str | None
    description: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoomTemplateBase(BaseSchema):
    name: str
    description: str | None = None
    entry_fee: Decimal
    max_cards_per_player: int = 1
    max_players: int
    min_players: int
    winning_pattern: str
    ball_calling_speed: int = 3
    house_percentage: Decimal
    referral_percentage: Decimal = Decimal("0.00")
    bonus_percentage: Decimal = Decimal("0.00")
    jackpot_percentage: Decimal = Decimal("0.00")
    visibility: str = "public"


class RoomTemplateCreate(RoomTemplateBase):
    pass


class RoomTemplateRead(RoomTemplateBase):
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoomBase(BaseSchema):
    template_id: UUID
    name: str


class RoomRead(RoomBase):
    id: UUID
    game_id: UUID | None = None
    status: str
    current_players: int
    cards_sold: int
    prize_pool: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
