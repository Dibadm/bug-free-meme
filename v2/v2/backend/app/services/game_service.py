from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from app.core.exceptions import ValidationError
from app.models.models import Game, GameStatus, CalledNumber
from app.repositories import GameRepository, CalledNumberRepository
from app.services.base import BaseService


class GameService(BaseService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.game_repo = GameRepository(db)
        self.called_number_repo = CalledNumberRepository(db)

    async def get_game(self, game_id: UUID) -> Game | None:
        return await self.game_repo.get_by_id(game_id)

    async def create_game(self, room_id: UUID, seed: str | None = None, seed_hash: str | None = None) -> Game:
        game = Game(room_id=room_id, status=GameStatus.WAITING, seed=seed, seed_hash=seed_hash)
        await self.db.add(game)
        await self.db.flush()
        await self.db.refresh(game)
        return game

    async def pause_game(self, game_id: UUID) -> Game | None:
        game = await self.game_repo.get_by_id(game_id)
        if not game:
            return None
        if game.status != GameStatus.RUNNING:
            raise ValidationError("Game is not running")

        game.status = GameStatus.PAUSED
        await self.db.flush()
        await self.db.refresh(game)
        return game

    async def resume_game(self, game_id: UUID) -> Game | None:
        game = await self.game_repo.get_by_id(game_id)
        if not game:
            return None
        if game.status != GameStatus.PAUSED:
            raise ValidationError("Game is not paused")

        game.status = GameStatus.RUNNING
        await self.db.flush()
        await self.db.refresh(game)
        return game

    async def cancel_game(self, game_id: UUID) -> Game | None:
        game = await self.game_repo.get_by_id(game_id)
        if not game:
            return None
        if game.status in (GameStatus.FINISHED, GameStatus.CANCELLED):
            raise ValidationError("Game is already finished or cancelled")

        game.status = GameStatus.CANCELLED
        game.finished_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(game)
        return game

    async def finish_game(self, game_id: UUID, winner_id: UUID | None, winning_pattern: str | None, prize_amount: Any) -> Game | None:
        game = await self.game_repo.get_by_id(game_id)
        if not game:
            return None
        if game.status == GameStatus.FINISHED:
            raise ValidationError("Game is already finished")

        game.status = GameStatus.FINISHED
        game.finished_at = datetime.now(timezone.utc)
        game.winner_id = winner_id
        game.winning_pattern = winning_pattern
        game.prize_amount = prize_amount
        await self.db.flush()
        await self.db.refresh(game)
        return game

    async def record_called_number(self, game_id: UUID, number: int) -> CalledNumber:
        called = CalledNumber(game_id=game_id, number=number)
        await self.db.add(called)
        game = await self.game_repo.get_by_id(game_id)
        if game:
            game.current_number = number
            if not game.started_at:
                game.started_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(called)
        return called
