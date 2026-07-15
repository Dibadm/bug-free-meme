from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from app.core.exceptions import ValidationError
from app.models.models import Announcement
from app.repositories import AnnouncementRepository
from app.services.base import BaseService


class AnnouncementService(BaseService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.announcement_repo = AnnouncementRepository(db)

    async def create_announcement(self, title: str, body: str, priority: int = 0) -> Announcement:
        if not title or not body:
            raise ValidationError("Title and body are required")

        announcement = Announcement(
            title=title,
            body=body,
            priority=priority,
            is_active=True,
        )
        return await self.announcement_repo.create(announcement)

    async def publish_announcement(self, announcement_id: UUID) -> Announcement | None:
        announcement = await self.announcement_repo.get_by_id(announcement_id)
        if not announcement:
            return None
        announcement.is_active = True
        announcement.published_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(announcement)
        return announcement

    async def deactivate_announcement(self, announcement_id: UUID) -> Announcement | None:
        announcement = await self.announcement_repo.get_by_id(announcement_id)
        if not announcement:
            return None
        announcement.is_active = False
        await self.db.flush()
        await self.db.refresh(announcement)
        return announcement

    async def get_active_announcements(self) -> list[Announcement]:
        return await self.announcement_repo.get_active_announcements()
