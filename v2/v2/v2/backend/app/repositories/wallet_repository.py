from __future__ import annotations

from decimal import Decimal
from sqlalchemy import select, func

from app.models.models import Wallet, WalletTransaction, WalletTransactionType
from app.repositories import BaseRepository


class WalletRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, Wallet)

    async def get_by_user_id(self, user_id: Any) -> Wallet | None:
        result = await self.db.execute(select(Wallet).where(Wallet.user_id == user_id))
        return result.scalar_one_or_none()

    async def get_balance(self, user_id: Any) -> Decimal:
        wallet = await self.get_by_user_id(user_id)
        return wallet.balance if wallet else Decimal("0.00")

    async def get_bonus_balance(self, user_id: Any) -> Decimal:
        wallet = await self.get_by_user_id(user_id)
        return wallet.bonus_balance if wallet else Decimal("0.00")

    async def get_jackpot_balance(self, user_id: Any) -> Decimal:
        wallet = await self.get_by_user_id(user_id)
        return wallet.jackpot_balance if wallet else Decimal("0.00")


class WalletTransactionRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, WalletTransaction)

    async def get_by_wallet_id(self, wallet_id: Any, limit: int = 100, offset: int = 0) -> list[WalletTransaction]:
        result = await self.db.execute(
            select(WalletTransaction)
            .where(WalletTransaction.wallet_id == wallet_id)
            .order_by(WalletTransaction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_by_type(self, wallet_id: Any, tx_type: WalletTransactionType) -> list[WalletTransaction]:
        result = await self.db.execute(
            select(WalletTransaction).where(WalletTransaction.wallet_id == wallet_id, WalletTransaction.type == tx_type)
        )
        return list(result.scalars().all())

    async def get_total_by_type(self, wallet_id: Any, tx_type: WalletTransactionType) -> Decimal:
        result = await self.db.execute(
            select(func.coalesce(func.sum(WalletTransaction.amount), 0)).where(
                WalletTransaction.wallet_id == wallet_id,
                WalletTransaction.type == tx_type,
                WalletTransaction.status == "completed",
            )
        )
        return result.scalar_one() or Decimal("0.00")
