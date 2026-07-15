from __future__ import annotations

from sqlalchemy import select

from app.models.models import Withdrawal, TransactionStatus
from app.repositories.base_repository import BaseRepository


class WithdrawalRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, Withdrawal)

    async def get_pending_withdrawals(self, limit: int = 100, offset: int = 0) -> list[Withdrawal]:
        result = await self.db.execute(
            select(Withdrawal)
            .where(Withdrawal.status == TransactionStatus.PENDING)
            .order_by(Withdrawal.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_by_user_id(self, user_id: Any, limit: int = 50, offset: int = 0) -> list[Withdrawal]:
        result = await self.db.execute(
            select(Withdrawal)
            .where(Withdrawal.user_id == user_id)
            .order_by(Withdrawal.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_pending_by_user(self, user_id: Any) -> list[Withdrawal]:
        result = await self.db.execute(
            select(Withdrawal).where(Withdrawal.user_id == user_id, Withdrawal.status == TransactionStatus.PENDING)
        )
        return list(result.scalars().all())
