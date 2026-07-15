from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from app.core.exceptions import ValidationError
from app.models.models import Deposit, TransactionStatus, WalletTransactionType
from app.repositories import DepositRepository, PaymentSettingsRepository
from app.services.base import BaseService
from app.services.wallet_service import WalletService


class DepositService(BaseService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.deposit_repo = DepositRepository(db)
        self.payment_repo = PaymentSettingsRepository(db)

    async def create_deposit(
        self,
        user_id: UUID,
        amount: Decimal,
        proof_url: str | None = None,
        sms_code: str | None = None,
    ) -> Deposit:
        if amount <= 0:
            raise ValidationError("Deposit amount must be positive")

        pending = await self.deposit_repo.get_pending_by_user(user_id)
        if pending:
            raise ValidationError("User already has a pending deposit")

        settings = await self.payment_repo.get_active()
        if not settings or not settings.is_deposit_enabled:
            raise ValidationError("Deposits are currently disabled")

        if amount < settings.min_deposit or amount > settings.max_deposit:
            raise ValidationError(f"Deposit amount must be between {settings.min_deposit} and {settings.max_deposit}")

        deposit = Deposit(
            user_id=user_id,
            amount=amount,
            proof_url=proof_url,
            sms_code=sms_code,
            status=TransactionStatus.PENDING,
        )
        return await self.deposit_repo.create(deposit)

    async def verify_sms(self, deposit_id: UUID, sms_text: str) -> Deposit:
        deposit = await self.deposit_repo.get_by_id(deposit_id)
        if not deposit:
            raise ValidationError("Deposit not found")
        if deposit.status != TransactionStatus.PENDING:
            raise ValidationError("Deposit is not pending")
        if deposit.sms_verified_at:
            raise ValidationError("SMS already verified for this deposit")

        settings = await self.payment_repo.get_active()
        if not settings:
            raise ValidationError("Payment settings not configured")

        if settings.telebirr_number not in sms_text:
            raise ValidationError("SMS does not contain the configured Telebirr number")

        deposit.sms_code = sms_text
        deposit.sms_sent_to = settings.telebirr_number
        deposit.sms_verified_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(deposit)

        if settings.auto_credit_enabled:
            await self._auto_credit(deposit, settings)

        return deposit

    async def _auto_credit(self, deposit: Deposit, settings: Any) -> None:
        wallet_service = WalletService(self.db)
        await wallet_service.credit(
            deposit.user_id,
            deposit.amount,
            WalletTransactionType.DEPOSIT,
            reference_id=str(deposit.id),
            description=f"Auto deposit via SMS verification",
        )
        deposit.status = TransactionStatus.COMPLETED
        deposit.reviewed_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(deposit)

    async def approve_deposit(self, deposit_id: UUID, approved_by: UUID) -> Deposit | None:
        deposit = await self.deposit_repo.get_by_id(deposit_id)
        if not deposit:
            return None
        if deposit.status != TransactionStatus.PENDING:
            raise ValidationError("Deposit is not pending")

        deposit.status = TransactionStatus.APPROVED
        deposit.reviewed_by = approved_by
        deposit.reviewed_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(deposit)
        return deposit

    async def reject_deposit(self, deposit_id: UUID, rejected_by: UUID, reason: str | None = None) -> Deposit | None:
        deposit = await self.deposit_repo.get_by_id(deposit_id)
        if not deposit:
            return None
        if deposit.status != TransactionStatus.PENDING:
            raise ValidationError("Deposit is not pending")

        deposit.status = TransactionStatus.REJECTED
        deposit.reviewed_by = rejected_by
        deposit.reviewed_at = datetime.now(timezone.utc)
        if reason:
            deposit.proof_url = reason
        await self.db.flush()
        await self.db.refresh(deposit)
        return deposit

    async def get_user_deposits(self, user_id: UUID, limit: int = 50, offset: int = 0) -> list[Deposit]:
        return await self.deposit_repo.get_by_user_id(user_id, limit=limit, offset=offset)
