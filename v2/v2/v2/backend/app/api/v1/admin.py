from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.models.models import Deposit, GameStatus, WalletTransactionType, Withdrawal
from app.schemas.admin import (
    AdminActionRead,
    AdminDashboard,
    AdminUserSearch,
    AuditLogRead,
    SearchUsersQuery,
    WalletAdjustment,
)
from app.schemas.wallet import DepositRead, WithdrawalRead
from app.services import AdminService, AuditService, DepositService, WithdrawalService, WalletService

router = APIRouter()


@router.get("/dashboard", response_model=AdminDashboard)
async def admin_dashboard(
    db: AsyncSession = Depends(get_db),
) -> AdminDashboard:
    from datetime import datetime, timedelta
    from decimal import Decimal
    from sqlalchemy import select, func
    from app.models.models import Deposit, Game, TransactionStatus, Wallet, Withdrawal

    today = datetime.utcnow().date()
    month_start = today.replace(day=1)

    revenue_today = await db.scalar(
        select(func.coalesce(func.sum(Deposit.amount), 0)).where(
            Deposit.status == TransactionStatus.APPROVED,
            func.date(Deposit.approved_at) == today,
        )
    )
    revenue_month = await db.scalar(
        select(func.coalesce(func.sum(Deposit.amount), 0)).where(
            Deposit.status == TransactionStatus.APPROVED,
            func.date(Deposit.approved_at) >= month_start,
        )
    )
    active_players = await db.scalar(
        select(func.count(func.distinct(Game.winner_id))).where(
            Game.status == GameStatus.RECOVERED
        )
    )
    active_games = await db.scalar(
        select(func.count(Game.id)).where(Game.status == GameStatus.RUNNING)
    )
    pending_withdrawals = await db.scalar(
        select(func.count(Withdrawal.id)).where(Withdrawal.status == TransactionStatus.PENDING)
    )

    house_wallet = await db.scalar(
        select(Wallet).where(Wallet.user_id == UUID("00000000-0000-0000-0000-000000000000"))
    )
    house_balance = house_wallet.balance if house_wallet else Decimal("0.00")

    return AdminDashboard(
        revenue_today=revenue_today or Decimal("0.00"),
        revenue_month=revenue_month or Decimal("0.00"),
        active_players=active_players or 0,
        active_games=active_games or 0,
        pending_withdrawals=pending_withdrawals or 0,
        house_balance=house_balance,
    )


@router.get("/users/search", response_model=list[AdminUserSearch])
async def search_users(
    query: SearchUsersQuery,
    db: AsyncSession = Depends(get_db),
) -> list[AdminUserSearch]:
    from sqlalchemy import select, or_
    from app.models.models import User, Wallet

    pattern = f"%{query.query}%"
    result = await db.execute(
        select(User, Wallet)
        .join(Wallet, User.id == Wallet.user_id, isouter=True)
        .where(
            or_(
                User.username.ilike(pattern),
                User.first_name.ilike(pattern),
                User.last_name.ilike(pattern),
                User.telegram_id.cast(str).ilike(pattern),
            )
        )
        .limit(query.page_size)
        .offset((query.page - 1) * query.page_size)
    )

    users = []
    for user, wallet in result.all():
        users.append(
            AdminUserSearch(
                id=user.id,
                telegram_id=user.telegram_id,
                username=user.username,
                first_name=user.first_name,
                wallet_balance=wallet.balance if wallet else Decimal("0.00"),
                status=user.status.value,
            )
        )
    return users


@router.post("/wallets/adjust")
async def adjust_wallet(
    adjustment: WalletAdjustment,
    admin_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    admin_service = AdminService(db)
    await admin_service.adjust_wallet(
        user_id=adjustment.user_id,
        amount=adjustment.amount,
        reason=adjustment.reason,
        performed_by=admin_id,
    )
    return {"status": "success"}


@router.get("/withdrawals", response_model=list[WithdrawalRead])
async def list_withdrawals(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[WithdrawalRead]:
    withdrawal_service = WithdrawalService(db)
    if status:
        from app.models.models import TransactionStatus
        withdrawals = await db.execute(
            select(Withdrawal).where(Withdrawal.status == TransactionStatus(status)).order_by(Withdrawal.created_at.desc())
        )
        return [WithdrawalRead.model_validate(w) for w in withdrawals.scalars().all()]
    withdrawals = await withdrawal_service.withdrawal_repo.get_all(limit=100)
    return [WithdrawalRead.model_validate(w) for w in withdrawals]


@router.post("/withdrawals/{withdrawal_id}/approve")
async def approve_withdrawal(
    withdrawal_id: UUID,
    admin_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    withdrawal_service = WithdrawalService(db)
    withdrawal = await withdrawal_service.approve_withdrawal(withdrawal_id, admin_id)
    if not withdrawal:
        raise HTTPException(status_code=404, detail="Withdrawal not found")

    audit = AuditService(db)
    await audit.log(
        actor_id=admin_id,
        action="withdrawal_approved",
        entity_type="withdrawal",
        entity_id=withdrawal_id,
    )
    return {"status": "approved"}


@router.post("/withdrawals/{withdrawal_id}/reject")
async def reject_withdrawal(
    withdrawal_id: UUID,
    admin_id: UUID,
    reason: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    withdrawal_service = WithdrawalService(db)
    wallet_service = WalletService(db)
    withdrawal = await withdrawal_service.reject_withdrawal(withdrawal_id, admin_id, reason)
    if not withdrawal:
        raise HTTPException(status_code=404, detail="Withdrawal not found")

    await wallet_service.credit(
        withdrawal.user_id,
        withdrawal.amount,
        WalletTransactionType.ADJUSTMENT,
        description=f"Withdrawal rejected: {reason}",
    )

    audit = AuditService(db)
    await audit.log(
        actor_id=admin_id,
        action="withdrawal_rejected",
        entity_type="withdrawal",
        entity_id=withdrawal_id,
        new_value={"reason": reason},
    )
    return {"status": "rejected"}


@router.get("/deposits", response_model=list[DepositRead])
async def list_deposits(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[DepositRead]:
    deposit_service = DepositService(db)
    if status:
        from app.models.models import TransactionStatus
        deposits = await db.execute(
            select(Deposit).where(Deposit.status == TransactionStatus(status)).order_by(Deposit.created_at.desc())
        )
        return [DepositRead.model_validate(d) for d in deposits.scalars().all()]
    deposits = await deposit_service.deposit_repo.get_all(limit=100)
    return [DepositRead.model_validate(d) for d in deposits]


@router.post("/deposits/{deposit_id}/approve")
async def approve_deposit(
    deposit_id: UUID,
    admin_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    deposit_service = DepositService(db)
    wallet_service = WalletService(db)
    deposit = await deposit_service.approve_deposit(deposit_id, admin_id)
    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")

    tx = await wallet_service.credit(
        deposit.user_id,
        deposit.amount,
        WalletTransactionType.DEPOSIT,
        reference_id=str(deposit.id),
        description="Deposit approved",
    )
    deposit.transaction_id = tx.id

    audit = AuditService(db)
    await audit.log(
        actor_id=admin_id,
        action="deposit_approved",
        entity_type="deposit",
        entity_id=deposit_id,
    )
    return {"status": "approved"}


@router.post("/deposits/{deposit_id}/reject")
async def reject_deposit(
    deposit_id: UUID,
    admin_id: UUID,
    reason: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    deposit_service = DepositService(db)
    deposit = await deposit_service.reject_deposit(deposit_id, admin_id, reason)
    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")

    audit = AuditService(db)
    await audit.log(
        actor_id=admin_id,
        action="deposit_rejected",
        entity_type="deposit",
        entity_id=deposit_id,
        new_value={"reason": reason},
    )
    return {"status": "rejected"}


@router.get("/audit-logs", response_model=list[AuditLogRead])
async def list_audit_logs(
    db: AsyncSession = Depends(get_db),
    limit: int = 100,
) -> list[AuditLogRead]:
    audit_service = AuditService(db)
    logs = await audit_service.get_recent_logs(limit=limit)
    return [AuditLogRead.model_validate(log) for log in logs]
