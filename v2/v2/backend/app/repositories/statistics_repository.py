from __future__ import annotations

from sqlalchemy import select

from app.models.models import PlayerStatistics
from app.repositories.base_repository import BaseRepository


class StatisticsRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, PlayerStatistics)

    async def get_by_user_id(self, user_id: Any) -> PlayerStatistics | None:
        result = await self.db.execute(
            select(PlayerStatistics).where(PlayerStatistics.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_top_players(self, limit: int = 10) -> list[PlayerStatistics]:
        result = await self.db.execute(
            select(PlayerStatistics)
            .where(PlayerStatistics.games_played > 0)
            .order_by(PlayerStatistics.win_rate.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
