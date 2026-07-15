from __future__ import annotations

from sqlalchemy import select

from app.models.models import Deposit, TransactionStatus
from app.repositories.base_repository import BaseRepository


class DepositRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, Deposit)

    async def get_pending_deposits(self, limit: int = 100, offset: int = 0) -> list[Deposit]:
        result = await self.db.execute(
            select(Deposit)
            .where(Deposit.status == TransactionStatus.PENDING)
            .order_by(Deposit.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_by_user_id(self, user_id: Any, limit: int = 50, offset: int = 0) -> list[Deposit]:
        result = await self.db.execute(
            select(Deposit)
            .where(Deposit.user_id == user_id)
            .order_by(Deposit.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_pending_by_user(self, user_id: Any) -> list[Deposit]:
        result = await self.db.execute(
            select(Deposit).where(Deposit.user_id == user_id, Deposit.status == TransactionStatus.PENDING)
        )
        return list(result.scalars().all())
