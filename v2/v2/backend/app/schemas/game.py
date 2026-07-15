from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas import BaseSchema


class GameBase(BaseSchema):
    room_id: UUID
    winning_pattern: str | None = None
    seed_hash: str | None = None


class GameCreate(BaseSchema):
    room_id: UUID
    seed: str
    seed_hash: str


class GameRead(GameBase):
    id: UUID
    status: str
    current_number: int | None = None
    called_numbers: list[int] | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    winner_id: UUID | None = None
    prize_amount: Decimal | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GameStartResponse(BaseSchema):
    game: GameRead
    seed: str
    seed_hash: str


class GameResult(BaseSchema):
    game_id: UUID
    winner_id: UUID
    winning_pattern: str
    prize_amount: Decimal
    called_numbers: list[int]
    seed: str


class CardBase(BaseSchema):
    room_id: UUID
    numbers: list[int]
    pattern_index: int


class CardRead(CardBase):
    id: UUID
    is_sold: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PurchasedCardBase(BaseSchema):
    game_id: UUID
    card_id: UUID
    user_id: UUID


class PurchasedCardRead(PurchasedCardBase):
    id: UUID
    marks: list[int] | None = None
    is_winner: bool = False
    purchased_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CalledNumberRead(BaseSchema):
    id: UUID
    game_id: UUID
    number: int
    called_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WinnerScreen(BaseSchema):
    is_winner: bool
    game_id: UUID
    prize_amount: Decimal | None = None
    winning_pattern: str | None = None
    winning_card: CardRead | None = None
    winner_username: str | None = None
    balance_after: Decimal
    called_numbers: list[int]
    seed: str | None = None


class LoserScreen(BaseSchema):
    is_winner: bool
    game_id: UUID
    winning_card_number: str | None = None
    winning_pattern: str | None = None
    masked_winner_username: str | None = None
    prize_amount: Decimal | None = None
    next_game_countdown: int | None = None
    called_numbers: list[int]
    seed: str | None = None
