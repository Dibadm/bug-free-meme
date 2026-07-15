from __future__ import annotations

from typing import Any
from uuid import UUID

from app.models.models import User, UserStatus
from app.repositories import UserRepository
from app.services.base import BaseService


class UserService(BaseService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.user_repo = UserRepository(db)

    async def get_or_create_user(self, telegram_id: int, **fields: Any) -> User:
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            user = User(telegram_id=telegram_id, **fields)
            return await self.user_repo.create(user)
        return user

    async def get_user(self, user_id: UUID) -> User | None:
        return await self.user_repo.get_by_id(user_id)

    async def update_user(self, user_id: UUID, **fields: Any) -> User | None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None
        return await self.user_repo.update(user, **fields)

    async def ban_user(self, user_id: UUID) -> User | None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None
        user.status = UserStatus.BANNED
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def activate_user(self, user_id: UUID) -> User | None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None
        user.status = UserStatus.ACTIVE
        await self.db.flush()
        await self.db.refresh(user)
        return user
