from __future__ import annotations

from typing import Any

from engine.src.application.game_service import GameService


class BallService:
    def __init__(self, game_service: GameService) -> None:
        self.game_service = game_service

    def call_number(self, game_id: Any) -> int | None:
        return self.game_service.call_number(game_id)

    def pause(self, game_id: Any) -> None:
        game = self.game_service.games.get(game_id)
        if game and game.metadata.get("ball_engine"):
            ball_engine = game.metadata["ball_engine"]
            ball_engine.pause()
            game.metadata["ball_engine"] = ball_engine.get_state()

    def resume(self, game_id: Any) -> None:
        game = self.game_service.games.get(game_id)
        if game and game.metadata.get("ball_engine"):
            ball_engine = game.metadata["ball_engine"]
            ball_engine.resume()
            game.metadata["ball_engine"] = ball_engine.get_state()
