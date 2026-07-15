from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

from app.models.models import (
    Wallet,
    WalletTransaction,
    WalletTransactionType,
    TransactionStatus,
)
from app.repositories import WalletRepository, WalletTransactionRepository
from app.services.base import BaseService


class WalletService(BaseService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.wallet_repo = WalletRepository(db)
        self.tx_repo = WalletTransactionRepository(db)

    async def get_balance(self, user_id: UUID) -> Decimal:
        return await self.wallet_repo.get_balance(user_id)

    async def credit(
        self,
        user_id: UUID,
        amount: Decimal,
        tx_type: WalletTransactionType,
        reference_id: str | None = None,
        description: str | None = None,
        tx_metadata: dict | None = None,
    ) -> WalletTransaction:
        if amount <= 0:
            raise ValueError("Amount must be positive")

        wallet = await self.wallet_repo.get_by_user_id(user_id)
        if not wallet:
            wallet = Wallet(user_id=user_id)
            await self.wallet_repo.create(wallet)

        balance_before = wallet.balance
        balance_after = balance_before + amount

        tx = WalletTransaction(
            wallet_id=wallet.id,
            type=tx_type,
            status=TransactionStatus.COMPLETED,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            reference_id=reference_id,
            description=description,
            tx_metadata=tx_metadata,
        )

        if tx_type == WalletTransactionType.DEPOSIT:
            wallet.balance = balance_after
            wallet.total_deposited = (wallet.total_deposited or Decimal("0.00")) + amount
        elif tx_type == WalletTransactionType.PRIZE:
            wallet.balance = balance_after
            wallet.total_won = (wallet.total_won or Decimal("0.00")) + amount
        elif tx_type == WalletTransactionType.REFERRAL:
            wallet.balance = balance_after
        elif tx_type == WalletTransactionType.BONUS:
            wallet.bonus_balance = (wallet.bonus_balance or Decimal("0.00")) + amount
        elif tx_type == WalletTransactionType.JACKPOT:
            wallet.jackpot_balance = (wallet.jackpot_balance or Decimal("0.00")) + amount

        await self.tx_repo.create(tx)
        return tx

    async def debit(
        self,
        user_id: UUID,
        amount: Decimal,
        tx_type: WalletTransactionType,
        reference_id: str | None = None,
        description: str | None = None,
        tx_metadata: dict | None = None,
    ) -> WalletTransaction:
        if amount <= 0:
            raise ValueError("Amount must be positive")

        wallet = await self.wallet_repo.get_by_user_id(user_id)
        if not wallet:
            raise ValueError("Wallet not found")

        if wallet.balance < amount:
            from app.core.exceptions import InsufficientBalanceError
            raise InsufficientBalanceError(f"Insufficient balance: {wallet.balance} < {amount}")

        balance_before = wallet.balance
        balance_after = balance_before - amount

        tx = WalletTransaction(
            wallet_id=wallet.id,
            type=tx_type,
            status=TransactionStatus.COMPLETED,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            reference_id=reference_id,
            description=description,
            tx_metadata=tx_metadata,
        )

        wallet.balance = balance_after
        wallet.total_spent = (wallet.total_spent or Decimal("0.00")) + amount

        await self.tx_repo.create(tx)
        return tx

    async def transfer(
        self,
        from_user_id: UUID,
        to_user_id: UUID,
        amount: Decimal,
        description: str | None = None,
    ) -> tuple[WalletTransaction, WalletTransaction]:
        if from_user_id == to_user_id:
            raise ValueError("Cannot transfer to self")
        if amount <= 0:
            raise ValueError("Amount must be positive")

        debit_tx = await self.debit(
            from_user_id,
            amount,
            WalletTransactionType.TRANSFER,
            description=description or f"Transfer to {to_user_id}",
        )
        credit_tx = await self.credit(
            to_user_id,
            amount,
            WalletTransactionType.TRANSFER,
            reference_id=str(debit_tx.id),
            description=description or f"Transfer from {from_user_id}",
        )
        return debit_tx, credit_tx
