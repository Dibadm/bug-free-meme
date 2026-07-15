from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

from app.models.models import Leaderboard
from app.repositories import LeaderboardRepository
from app.services.base import BaseService


class LeaderboardService(BaseService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.leaderboard_repo = LeaderboardRepository(db)

    async def update_score(self, user_id: UUID, period: str, score_delta: Decimal) -> Leaderboard:
        entry = await self.leaderboard_repo.get_user_rank(user_id, period)
        if not entry:
            entry = Leaderboard(user_id=user_id, period=period, score=score_delta)
            return await self.leaderboard_repo.create(entry)

        entry.score = (entry.score or Decimal("0.00")) + score_delta
        await self.db.flush()
        await self.db.refresh(entry)
        return entry

    async def get_top_players(self, period: str, limit: int = 10) -> list[Leaderboard]:
        return await self.leaderboard_repo.get_top_users(period, limit=limit)
