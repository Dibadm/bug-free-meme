from __future__ import annotations

import pytest
from decimal import Decimal
from uuid import uuid4

from app.core.exceptions import InsufficientBalanceError, ValidationError
from app.models.models import WalletTransactionType
from app.services import WalletService


@pytest.mark.asyncio
async def test_wallet_credit(db_session: Any) -> None:
    service = WalletService(db_session)
    user_id = uuid4()
    tx = await service.credit(user_id, Decimal("100.00"), WalletTransactionType.DEPOSIT)
    assert tx.amount == Decimal("100.00")
    assert tx.balance_after == Decimal("100.00")
    balance = await service.get_balance(user_id)
    assert balance == Decimal("100.00")


@pytest.mark.asyncio
async def test_wallet_debit(db_session: Any) -> None:
    service = WalletService(db_session)
    user_id = uuid4()
    await service.credit(user_id, Decimal("100.00"), WalletTransactionType.DEPOSIT)
    tx = await service.debit(user_id, Decimal("50.00"), WalletTransactionType.PURCHASE)
    assert tx.amount == Decimal("50.00")
    assert tx.balance_after == Decimal("50.00")


@pytest.mark.asyncio
async def test_wallet_debit_insufficient_balance(db_session: Any) -> None:
    service = WalletService(db_session)
    user_id = uuid4()
    with pytest.raises(InsufficientBalanceError):
        await service.debit(user_id, Decimal("10.00"), WalletTransactionType.PURCHASE)


@pytest.mark.asyncio
async def test_wallet_transfer(db_session: Any) -> None:
    from app.services import TransferService

    service = TransferService(db_session)
    from_id = uuid4()
    to_id = uuid4()
    await service.wallet_service.credit(from_id, Decimal("100.00"), WalletTransactionType.DEPOSIT)
    debit_tx, credit_tx = await service.transfer(from_id, to_id, Decimal("30.00"))
    assert debit_tx.amount == Decimal("30.00")
    assert credit_tx.amount == Decimal("30.00")
    assert await service.wallet_service.get_balance(to_id) == Decimal("30.00")


@pytest.mark.asyncio
async def test_wallet_credit_negative_amount(db_session: Any) -> None:
    service = WalletService(db_session)
    with pytest.raises(ValueError, match="Amount must be positive"):
        await service.credit(uuid4(), Decimal("-10.00"), WalletTransactionType.DEPOSIT)
