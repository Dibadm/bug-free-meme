from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel


class EventType(str, Enum):
    ROOM_CREATED = "room.created"
    ROOM_UPDATED = "room.updated"
    ROOM_DELETED = "room.deleted"
    PLAYER_JOINED = "player.joined"
    PLAYER_LEFT = "player.left"
    CARD_PURCHASED = "card.purchased"
    CARD_AVAILABLE = "card.available"
    COUNTDOWN_STARTED = "countdown.started"
    COUNTDOWN_TICK = "countdown.tick"
    COUNTDOWN_ENDED = "countdown.ended"
    BALL_CALLED = "ball.called"
    BALLS_ANIMATED = "balls.animated"
    MARK_AUTO = "mark.auto"
    MARK_MANUAL = "mark.manual"
    WINNER_CLAIMED = "winner.claimed"
    WINNER_VALIDATED = "winner.validated"
    PRIZE_DISTRIBUTED = "prize.distributed"
    GAME_COMPLETED = "game.completed"
    GAME_PAUSED = "game.paused"
    GAME_RESUMED = "game.resumed"
    GAME_CANCELLED = "game.cancelled"
    LEADERBOARD_UPDATED = "leaderboard.updated"
    WALLET_UPDATED = "wallet.updated"
    ANNOUNCEMENT = "announcement"
    NOTIFICATION = "notification"
    CONNECTION_STATE = "connection.state"
    USER_PRESENCE = "user.presence"
    PAYMENT_SETTINGS_UPDATED = "payment.settings.updated"
    ERROR = "error"


class WebSocketMessage(BaseModel):
    event: str
    data: dict[str, Any]
    room_id: str | None = None
    user_id: str | None = None
    timestamp: str
    id: str
