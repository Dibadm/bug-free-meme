from __future__ import annotations

from sqlalchemy import select

from app.models.models import User
from app.repositories import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, User)

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()

    async def get_active_users(self, limit: int = 100, offset: int = 0) -> list[User]:
        result = await self.db.execute(
            select(User).where(User.status == "active", User.deleted_at.is_(None)).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def get_admin_users(self) -> list[User]:
        result = await self.db.execute(select(User).where(User.is_admin == True, User.deleted_at.is_(None)))
        return list(result.scalars().all())
