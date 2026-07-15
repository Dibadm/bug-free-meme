from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from app.core.exceptions import ValidationError
from app.models.models import Withdrawal, TransactionStatus, WalletTransactionType
from app.repositories import WithdrawalRepository
from app.services.base import BaseService


class WithdrawalService(BaseService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.withdrawal_repo = WithdrawalRepository(db)

    async def create_withdrawal(self, user_id: UUID, amount: Decimal, phone_number: str) -> Withdrawal:
        if amount <= 0:
            raise ValidationError("Withdrawal amount must be positive")

        pending = await self.withdrawal_repo.get_pending_by_user(user_id)
        if pending:
            raise ValidationError("User already has a pending withdrawal")

        withdrawal = Withdrawal(
            user_id=user_id,
            amount=amount,
            phone_number=phone_number,
            status=TransactionStatus.PENDING,
        )
        return await self.withdrawal_repo.create(withdrawal)

    async def approve_withdrawal(self, withdrawal_id: UUID, approved_by: UUID) -> Withdrawal | None:
        withdrawal = await self.withdrawal_repo.get_by_id(withdrawal_id)
        if not withdrawal:
            return None
        if withdrawal.status != TransactionStatus.PENDING:
            raise ValidationError("Withdrawal is not pending")

        withdrawal.status = TransactionStatus.APPROVED
        withdrawal.reviewed_by = approved_by
        withdrawal.reviewed_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(withdrawal)
        return withdrawal

    async def reject_withdrawal(self, withdrawal_id: UUID, rejected_by: UUID, reason: str | None = None) -> Withdrawal | None:
        withdrawal = await self.withdrawal_repo.get_by_id(withdrawal_id)
        if not withdrawal:
            return None
        if withdrawal.status != TransactionStatus.PENDING:
            raise ValidationError("Withdrawal is not pending")

        withdrawal.status = TransactionStatus.REJECTED
        withdrawal.reviewed_by = rejected_by
        withdrawal.reviewed_at = datetime.now(timezone.utc)
        if reason:
            withdrawal.rejection_reason = reason
        await self.db.flush()
        await self.db.refresh(withdrawal)
        return withdrawal

    async def get_user_withdrawals(self, user_id: UUID, limit: int = 50, offset: int = 0) -> list[Withdrawal]:
        return await self.withdrawal_repo.get_by_user_id(user_id, limit=limit, offset=offset)
