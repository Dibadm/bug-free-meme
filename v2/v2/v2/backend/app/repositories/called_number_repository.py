from __future__ import annotations

from sqlalchemy import select

from app.models.models import CalledNumber
from app.repositories import BaseRepository


class CalledNumberRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, CalledNumber)

    async def get_by_game_id(self, game_id: Any) -> list[CalledNumber]:
        result = await self.db.execute(
            select(CalledNumber).where(CalledNumber.game_id == game_id).order_by(CalledNumber.called_at.asc())
        )
        return list(result.scalars().all())

    async def get_last_called(self, game_id: Any) -> CalledNumber | None:
        result = await self.db.execute(
            select(CalledNumber).where(CalledNumber.game_id == game_id).order_by(CalledNumber.called_at.desc()).limit(1)
        )
        return result.scalar_one_or_none()
