from __future__ import annotations

from sqlalchemy import select

from app.models.models import DailyReward
from app.repositories import BaseRepository


class DailyRewardRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, DailyReward)

    async def get_by_user_id(self, user_id: Any, limit: int = 50, offset: int = 0) -> list[DailyReward]:
        result = await self.db.execute(
            select(DailyReward)
            .where(DailyReward.user_id == user_id)
            .order_by(DailyReward.claimed_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_user_reward_for_day(self, user_id: Any, day: int) -> DailyReward | None:
        result = await self.db.execute(
            select(DailyReward).where(DailyReward.user_id == user_id, DailyReward.day == day)
        )
        return result.scalar_one_or_none()
