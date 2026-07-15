from __future__ import annotations

from sqlalchemy import select

from app.models.models import Leaderboard
from app.repositories import BaseRepository


class LeaderboardRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, Leaderboard)

    async def get_by_period(self, period: str, limit: int = 100) -> list[Leaderboard]:
        result = await self.db.execute(
            select(Leaderboard)
            .where(Leaderboard.period == period)
            .order_by(Leaderboard.rank.asc().nulls_last())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_user_rank(self, user_id: Any, period: str) -> Leaderboard | None:
        result = await self.db.execute(
            select(Leaderboard).where(Leaderboard.user_id == user_id, Leaderboard.period == period)
        )
        return result.scalar_one_or_none()

    async def get_top_users(self, period: str, limit: int = 10) -> list[Leaderboard]:
        result = await self.db.execute(
            select(Leaderboard)
            .where(Leaderboard.period == period)
            .order_by(Leaderboard.score.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
