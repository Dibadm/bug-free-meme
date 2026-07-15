from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from app.core.exceptions import ValidationError
from app.models.models import Achievement, AchievementProgress
from app.repositories import AchievementRepository, AchievementProgressRepository
from app.services.base import BaseService


class AchievementService(BaseService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.achievement_repo = AchievementRepository(db)
        self.progress_repo = AchievementProgressRepository(db)

    async def create_achievement(self, **fields: Any) -> Achievement:
        if not fields.get("name") or not fields.get("description"):
            raise ValidationError("Name and description are required")
        if fields.get("threshold", 0) <= 0:
            raise ValidationError("Threshold must be positive")

        achievement = Achievement(**fields)
        return await self.achievement_repo.create(achievement)

    async def get_active_achievements(self) -> list[Achievement]:
        return await self.achievement_repo.get_active_achievements()

    async def get_user_progress(self, user_id: UUID) -> list[AchievementProgress]:
        return await self.progress_repo.get_by_user_id(user_id)

    async def update_progress(self, user_id: UUID, achievement_id: UUID, current_value: int) -> AchievementProgress | None:
        progress = await self.progress_repo.get_by_user_and_achievement(user_id, achievement_id)
        if not progress:
            achievement = await self.achievement_repo.get_by_id(achievement_id)
            if not achievement:
                return None
            progress = AchievementProgress(user_id=user_id, achievement_id=achievement_id, current_value=current_value)
            return await self.progress_repo.create(progress)

        progress.current_value = current_value
        achievement = await self.achievement_repo.get_by_id(achievement_id)
        if achievement and current_value >= achievement.threshold:
            progress.is_completed = True
            progress.completed_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(progress)
        return progress
