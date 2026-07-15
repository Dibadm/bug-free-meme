from __future__ import annotations

from typing import Any

from engine.src.application.game_service import GameService


class RoomService:
    def __init__(self, game_service: GameService) -> None:
        self.game_service = game_service

    def create_room(self, room_id: Any, name: str, entry_fee: float, max_players: int, min_players: int, winning_pattern: str, ball_interval_seconds: int = 3, visibility: str = "public") -> Any:
        return self.game_service.create_room(room_id, name, entry_fee, max_players, min_players, winning_pattern, ball_interval_seconds, visibility)

    def get_room_state(self, room_id: Any) -> dict[str, Any] | None:
        room = self.game_service.rooms.get(room_id)
        if not room:
            return None
        return {
            "id": str(room.room_id),
            "name": room.name,
            "entry_fee": room.entry_fee,
            "max_players": room.max_players,
            "min_players": room.min_players,
            "winning_pattern": room.winning_pattern,
            "ball_interval_seconds": room.ball_interval_seconds,
            "status": room.status.value,
            "current_players": room.current_players,
            "cards_sold": room.cards_sold,
            "prize_pool": room.prize_pool,
        }
