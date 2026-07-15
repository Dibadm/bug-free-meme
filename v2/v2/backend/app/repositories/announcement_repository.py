from __future__ import annotations

from sqlalchemy import select

from app.models.models import Announcement
from app.repositories.base_repository import BaseRepository


class AnnouncementRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, Announcement)

    async def get_active_announcements(self) -> list[Announcement]:
        result = await self.db.execute(
            select(Announcement)
            .where(Announcement.is_active == True, Announcement.deleted_at.is_(None))
            .order_by(Announcement.priority.desc(), Announcement.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_all_active(self, limit: int = 50, offset: int = 0) -> list[Announcement]:
        result = await self.db.execute(
            select(Announcement)
            .where(Announcement.is_active == True, Announcement.deleted_at.is_(None))
            .order_by(Announcement.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
