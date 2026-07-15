from __future__ import annotations

from sqlalchemy import select

from app.models.models import SystemLog
from app.repositories import BaseRepository


class SystemLogRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, SystemLog)

    async def get_by_level(self, level: str, limit: int = 100, offset: int = 0) -> list[SystemLog]:
        result = await self.db.execute(
            select(SystemLog)
            .where(SystemLog.level == level)
            .order_by(SystemLog.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_recent(self, limit: int = 100) -> list[SystemLog]:
        result = await self.db.execute(
            select(SystemLog).order_by(SystemLog.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())
