from __future__ import annotations

from sqlalchemy import select

from app.models.models import PrizePayout
from app.repositories.base_repository import BaseRepository


class PrizePayoutRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, PrizePayout)

    async def get_by_game_id(self, game_id: Any) -> list[PrizePayout]:
        result = await self.db.execute(
            select(PrizePayout).where(PrizePayout.game_id == game_id)
        )
        return list(result.scalars().all())

    async def get_by_user_id(self, user_id: Any, limit: int = 50, offset: int = 0) -> list[PrizePayout]:
        result = await self.db.execute(
            select(PrizePayout)
            .where(PrizePayout.user_id == user_id)
            .order_by(PrizePayout.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
