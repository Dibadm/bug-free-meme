from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.schemas.wallet import (
    DepositCreate,
    DepositRead,
    SMSVerifyRequest,
    TransferCreate,
    WalletAdjustment,
    WalletTransactionCreate,
    WithdrawalCreate,
    WithdrawalRead,
)
from app.services import DepositService, TransferService, WalletService, WithdrawalService
from app.services.wallet_service import InsufficientBalanceError, WalletTransactionType

router = APIRouter()


@router.get("/balance", response_model=dict)
async def get_balance(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, float]:
    service = WalletService(db)
    balance = await service.get_balance(user_id)
    return {"balance": float(balance)}


@router.post("/deposit", response_model=DepositRead)
async def create_deposit(
    deposit_data: DepositCreate,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> DepositRead:
    service = DepositService(db)
    deposit = await service.create_deposit(user_id, deposit_data.amount, deposit_data.proof_url, deposit_data.sms_code)
    return DepositRead.model_validate(deposit)


@router.post("/deposit/verify-sms", response_model=DepositRead)
async def verify_sms(
    sms_data: SMSVerifyRequest,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> DepositRead:
    service = DepositService(db)
    deposit = await service.verify_sms(sms_data.deposit_id, sms_data.sms_text)
    if deposit.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return DepositRead.model_validate(deposit)


@router.post("/withdraw", response_model=WithdrawalRead)
async def create_withdrawal(
    withdrawal_data: WithdrawalCreate,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> WithdrawalRead:
    wallet_service = WalletService(db)
    try:
        await wallet_service.debit(
            user_id,
            withdrawal_data.amount,
            WalletTransactionType.WITHDRAWAL,
            description=f"Withdrawal to {withdrawal_data.phone_number}",
        )
    except InsufficientBalanceError:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    withdrawal_service = WithdrawalService(db)
    withdrawal = await withdrawal_service.create_withdrawal(
        user_id, withdrawal_data.amount, withdrawal_data.phone_number
    )
    return WithdrawalRead.model_validate(withdrawal)


@router.post("/transfer")
async def transfer(
    transfer_data: TransferCreate,
    from_user_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    service = TransferService(db)
    try:
        await service.transfer(from_user_id, transfer_data.to_user_id, transfer_data.amount)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "success"}
