from __future__ import annotations

from sqlalchemy import select

from app.models.models import AdminAction
from app.repositories.base_repository import BaseRepository


class AdminActionRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, AdminAction)

    async def get_by_admin_id(self, admin_id: Any, limit: int = 100, offset: int = 0) -> list[AdminAction]:
        result = await self.db.execute(
            select(AdminAction)
            .where(AdminAction.admin_id == admin_id)
            .order_by(AdminAction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_recent(self, limit: int = 100) -> list[AdminAction]:
        result = await self.db.execute(
            select(AdminAction).order_by(AdminAction.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())
