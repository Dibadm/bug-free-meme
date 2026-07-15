from __future__ import annotations

from sqlalchemy import select

from app.models.models import Achievement, AchievementProgress
from app.repositories import BaseRepository


class AchievementRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, Achievement)

    async def get_active_achievements(self) -> list[Achievement]:
        result = await self.db.execute(
            select(Achievement).where(Achievement.is_active == True)
        )
        return list(result.scalars().all())

    async def get_by_type(self, achievement_type: str) -> list[Achievement]:
        result = await self.db.execute(
            select(Achievement).where(Achievement.type == achievement_type, Achievement.is_active == True)
        )
        return list(result.scalars().all())


class AchievementProgressRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, AchievementProgress)

    async def get_by_user_id(self, user_id: Any) -> list[AchievementProgress]:
        result = await self.db.execute(
            select(AchievementProgress).where(AchievementProgress.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_by_user_and_achievement(self, user_id: Any, achievement_id: Any) -> AchievementProgress | None:
        result = await self.db.execute(
            select(AchievementProgress).where(
                AchievementProgress.user_id == user_id,
                AchievementProgress.achievement_id == achievement_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_completed_by_user(self, user_id: Any) -> list[AchievementProgress]:
        result = await self.db.execute(
            select(AchievementProgress).where(
                AchievementProgress.user_id == user_id,
                AchievementProgress.is_completed == True,
            )
        )
        return list(result.scalars().all())
