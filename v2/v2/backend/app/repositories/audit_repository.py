from __future__ import annotations

from sqlalchemy import select

from app.models.models import AuditLog
from app.repositories.base_repository import BaseRepository


class AuditRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, AuditLog)

    async def get_by_actor_id(self, actor_id: Any, limit: int = 100, offset: int = 0) -> list[AuditLog]:
        result = await self.db.execute(
            select(AuditLog)
            .where(AuditLog.actor_id == actor_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_by_entity(self, entity_type: str, entity_id: Any) -> list[AuditLog]:
        result = await self.db.execute(
            select(AuditLog)
            .where(AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id)
            .order_by(AuditLog.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_recent(self, limit: int = 100) -> list[AuditLog]:
        result = await self.db.execute(
            select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())
