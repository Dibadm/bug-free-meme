from __future__ import annotations

from sqlalchemy import select

from app.models.models import NotificationPreference
from app.repositories.base_repository import BaseRepository


class NotificationPreferenceRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, NotificationPreference)

    async def get_by_user_id(self, user_id: Any) -> list[NotificationPreference]:
        result = await self.db.execute(
            select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_by_user_and_type(self, user_id: Any, notification_type: str) -> NotificationPreference | None:
        result = await self.db.execute(
            select(NotificationPreference).where(
                NotificationPreference.user_id == user_id,
                NotificationPreference.notification_type == notification_type,
            )
        )
        return result.scalar_one_or_none()
