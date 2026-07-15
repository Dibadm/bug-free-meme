from __future__ import annotations

from typing import Any

from engine.src.application.game_service import GameService


class PlayerService:
    def __init__(self, game_service: GameService) -> None:
        self.game_service = game_service

    def join_player(self, room_id: Any, user_id: Any, cards: list[Any]) -> None:
        self.game_service.join_player(room_id, user_id, cards)

    def leave_player(self, room_id: Any, user_id: Any) -> None:
        room = self.game_service.rooms.get(room_id)
        if not room:
            return
        player = room.players.get(user_id)
        if not player:
            return
        player.left_at = datetime.now(timezone.utc)
        player.is_connected = False
        room.current_players = sum(1 for p in room.players.values() if p.is_connected)

    def mark_card(self, game_id: Any, user_id: Any, card_id: Any, number: int, auto: bool = True) -> bool:
        return self.game_service.mark_card(game_id, user_id, card_id, number, auto)
