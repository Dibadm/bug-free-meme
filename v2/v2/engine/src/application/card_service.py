from __future__ import annotations

from typing import Any

from engine.src.application.game_service import GameService


class CardService:
    def __init__(self, game_service: GameService) -> None:
        self.game_service = game_service

    def generate_cards(self, room_id: Any, count: int, pattern_index: int = 0) -> list[Any]:
        return self.game_service.card_engine.generate_cards(room_id, count, pattern_index)

    def validate_card(self, card: Any) -> bool:
        return self.game_service.card_engine.validate_card(card)
