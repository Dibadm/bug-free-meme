from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

from app.models.models import WalletTransactionType
from app.services.base import BaseService
from app.services.wallet_service import WalletService


class TransferService(BaseService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.wallet_service = WalletService(db)

    async def transfer(
        self,
        from_user_id: UUID,
        to_user_id: UUID,
        amount: Decimal,
        description: str | None = None,
    ) -> tuple[WalletTransaction, WalletTransaction]:
        return await self.wallet_service.transfer(from_user_id, to_user_id, amount, description)
