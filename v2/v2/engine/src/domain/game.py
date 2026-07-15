from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class GameLifecycleState(str, Enum):
    CREATED = "created"
    WAITING = "waiting"
    SELLING_CARDS = "selling_cards"
    LOCKED = "locked"
    STARTING = "starting"
    CALLING_NUMBERS = "calling_numbers"
    PAUSED = "paused"
    WINNER_VALIDATION = "winner_validation"
    PRIZE_DISTRIBUTION = "prize_distribution"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RECOVERED = "recovered"
    ARCHIVED = "archived"


VALID_TRANSITIONS: dict[GameLifecycleState, set[GameLifecycleState]] = {
    GameLifecycleState.CREATED: {GameLifecycleState.WAITING, GameLifecycleState.CANCELLED},
    GameLifecycleState.WAITING: {GameLifecycleState.SELLING_CARDS, GameLifecycleState.CANCELLED},
    GameLifecycleState.SELLING_CARDS: {GameLifecycleState.LOCKED, GameLifecycleState.CANCELLED},
    GameLifecycleState.LOCKED: {GameLifecycleState.STARTING, GameLifecycleState.SELLING_CARDS, GameLifecycleState.CANCELLED},
    GameLifecycleState.STARTING: {GameLifecycleState.CALLING_NUMBERS, GameLifecycleState.CANCELLED},
    GameLifecycleState.CALLING_NUMBERS: {GameLifecycleState.PAUSED, GameLifecycleState.WINNER_VALIDATION, GameLifecycleState.CANCELLED},
    GameLifecycleState.PAUSED: {GameLifecycleState.CALLING_NUMBERS, GameLifecycleState.CANCELLED},
    GameLifecycleState.WINNER_VALIDATION: {GameLifecycleState.PRIZE_DISTRIBUTION, GameLifecycleState.CANCELLED},
    GameLifecycleState.PRIZE_DISTRIBUTION: {GameLifecycleState.COMPLETED, GameLifecycleState.CANCELLED},
    GameLifecycleState.COMPLETED: {GameLifecycleState.ARCHIVED},
    GameLifecycleState.CANCELLED: {GameLifecycleState.ARCHIVED},
    GameLifecycleState.RECOVERED: {GameLifecycleState.CALLING_NUMBERS, GameLifecycleState.PAUSED, GameLifecycleState.CANCELLED},
    GameLifecycleState.ARCHIVED: set(),
}


@dataclass
class GameState:
    game_id: UUID = field(default_factory=uuid4)
    room_id: UUID = field(default_factory=uuid4)
    state: GameLifecycleState = GameLifecycleState.CREATED
    seed: str = ""
    seed_hash: str = ""
    called_numbers: list[int] = field(default_factory=list)
    current_number: int | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    winner_id: UUID | None = None
    winning_pattern: str | None = None
    prize_amount: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def transition_to(self, new_state: GameLifecycleState) -> None:
        allowed = VALID_TRANSITIONS.get(self.state, set())
        if new_state not in allowed:
            raise ValueError(f"Illegal state transition: {self.state.value} -> {new_state.value}")
        self.state = new_state


@dataclass
class PlayerState:
    user_id: UUID = field(default_factory=uuid4)
    cards: list[UUID] = field(default_factory=list)
    joined_at: datetime | None = None
    left_at: datetime | None = None
    is_connected: bool = True
    auto_mark_enabled: bool = True


@dataclass
class RoomState:
    room_id: UUID = field(default_factory=uuid4)
    name: str = ""
    entry_fee: float = 0.0
    max_players: int = 0
    min_players: int = 0
    winning_pattern: str = ""
    ball_interval_seconds: int = 3
    visibility: str = "public"
    status: GameLifecycleState = GameLifecycleState.WAITING
    current_players: int = 0
    cards_sold: int = 0
    prize_pool: float = 0.0
    players: dict[UUID, PlayerState] = field(default_factory=dict)
    cards: dict[UUID, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
