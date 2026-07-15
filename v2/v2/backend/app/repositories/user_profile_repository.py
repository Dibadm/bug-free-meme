from __future__ import annotations

from sqlalchemy import select

from app.models.models import UserProfile
from app.repositories.base_repository import BaseRepository


class UserProfileRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, UserProfile)

    async def get_by_user_id(self, user_id: Any) -> UserProfile | None:
        result = await self.db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
        return result.scalar_one_or_none()
