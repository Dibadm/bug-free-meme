from __future__ import annotations

from typing import Any

from engine.src.application.game_service import GameService


class PrizeService:
    def __init__(self, game_service: GameService) -> None:
        self.game_service = game_service

    def calculate_prize(self, room_id: Any, winner_count: int) -> dict[str, Any]:
        room = self.game_service.rooms.get(room_id)
        if not room:
            return {}
        prize_pool = room.prize_pool
        house_percentage = 0.0
        referral_percentage = 0.0
        bonus_percentage = 0.0
        jackpot_percentage = 0.0
        winner_amount = prize_pool * (1 - (house_percentage + referral_percentage + bonus_percentage + jackpot_percentage) / 100)
        return {
            "prize_pool": prize_pool,
            "house_percentage": house_percentage,
            "referral_percentage": referral_percentage,
            "bonus_percentage": bonus_percentage,
            "jackpot_percentage": jackpot_percentage,
            "winner_amount": winner_amount / max(winner_count, 1),
            "house_amount": prize_pool * house_percentage / 100,
        }

    def distribute_prize(self, game_id: Any, winners: list[dict[str, Any]]) -> dict[str, Any]:
        game = self.game_service.games.get(game_id)
        if not game:
            return {}
        room = self.game_service.rooms.get(game.room_id)
        if not room:
            return {}
        prize_per_winner = room.prize_pool / max(len(winners), 1)
        return {
            "game_id": str(game_id),
            "total_prize": room.prize_pool,
            "winner_count": len(winners),
            "prize_per_winner": prize_per_winner,
            "winners": [{"user_id": str(w["user_id"]), "amount": prize_per_winner} for w in winners],
        }
