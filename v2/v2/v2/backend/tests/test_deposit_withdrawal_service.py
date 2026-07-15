from __future__ import annotations

import pytest
from decimal import Decimal
from uuid import uuid4

from app.core.exceptions import ValidationError
from app.models.models import TransactionStatus
from app.services import DepositService, WithdrawalService


@pytest.mark.asyncio
async def test_create_deposit(db_session: Any) -> None:
    service = DepositService(db_session)
    user_id = uuid4()
    deposit = await service.create_deposit(user_id, Decimal("500.00"), proof_url="https://example.com/proof")
    assert deposit.amount == Decimal("500.00")
    assert deposit.status == TransactionStatus.PENDING
    assert deposit.proof_url == "https://example.com/proof"


@pytest.mark.asyncio
async def test_create_duplicate_deposit_fails(db_session: Any) -> None:
    service = DepositService(db_session)
    user_id = uuid4()
    await service.create_deposit(user_id, Decimal("500.00"))
    with pytest.raises(ValidationError, match="pending deposit"):
        await service.create_deposit(user_id, Decimal("300.00"))


@pytest.mark.asyncio
async def test_approve_deposit(db_session: Any) -> None:
    service = DepositService(db_session)
    user_id = uuid4()
    deposit = await service.create_deposit(user_id, Decimal("500.00"))
    approved = await service.approve_deposit(deposit.id, approved_by=uuid4())
    assert approved.status == TransactionStatus.APPROVED
    assert approved.reviewed_by is not None


@pytest.mark.asyncio
async def test_reject_deposit(db_session: Any) -> None:
    service = DepositService(db_session)
    user_id = uuid4()
    deposit = await service.create_deposit(user_id, Decimal("500.00"))
    rejected = await service.reject_deposit(deposit.id, rejected_by=uuid4(), reason="Invalid proof")
    assert rejected.status == TransactionStatus.REJECTED


@pytest.mark.asyncio
async def test_withdraw_service(db_session: Any) -> None:
    from app.services import WalletService

    wallet_service = WalletService(db_session)
    service = WithdrawalService(db_session)
    user_id = uuid4()
    await wallet_service.credit(user_id, Decimal("1000.00"), WalletTransactionType.DEPOSIT)

    withdrawal = await service.create_withdrawal(user_id, Decimal("500.00"), phone_number="0912345678")
    assert withdrawal.amount == Decimal("500.00")
    assert withdrawal.status == TransactionStatus.PENDING


@pytest.mark.asyncio
async def test_withdraw_duplicate_fails(db_session: Any) -> None:
    from app.services import WalletService

    wallet_service = WalletService(db_session)
    service = WithdrawalService(db_session)
    user_id = uuid4()
    await wallet_service.credit(user_id, Decimal("1000.00"), WalletTransactionType.DEPOSIT)
    await service.create_withdrawal(user_id, Decimal("500.00"), phone_number="0912345678")
    with pytest.raises(ValidationError, match="pending withdrawal"):
        await service.create_withdrawal(user_id, Decimal("300.00"), phone_number="0912345678")
