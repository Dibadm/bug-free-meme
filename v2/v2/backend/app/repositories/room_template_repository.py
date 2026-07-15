from __future__ import annotations

from sqlalchemy import select

from app.models.models import RoomTemplate, RoomStatus
from app.repositories.base_repository import BaseRepository


class RoomTemplateRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, RoomTemplate)

    async def get_active_templates(self) -> list[RoomTemplate]:
        result = await self.db.execute(
            select(RoomTemplate).where(RoomTemplate.status == RoomStatus.ACTIVE, RoomTemplate.deleted_at.is_(None))
        )
        return list(result.scalars().all())

    async def get_by_winning_pattern(self, pattern: str) -> list[RoomTemplate]:
        result = await self.db.execute(
            select(RoomTemplate).where(RoomTemplate.winning_pattern == pattern, RoomTemplate.deleted_at.is_(None))
        )
        return list(result.scalars().all())

    async def exists_by_name(self, name: str) -> bool:
        return await self.exists(name=name, deleted_at=None)
