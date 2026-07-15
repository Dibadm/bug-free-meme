from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.models import Game, GameStatus, Room, RoomStatus, TransactionStatus, Wallet, Deposit, Withdrawal
from app.schemas.admin import (
    AdminActionRead,
    AdminDashboard,
    AdminUserSearch,
    AuditLogRead,
    SearchUsersQuery,
    WalletAdjustment,
    RoomControl,
    AnnouncementCreate,
    FeatureFlagUpdate,
    MaintenanceModeUpdate,
    ReportExport,
)
from app.services import AdminService, AuditService, DepositService, WithdrawalService, WalletService

router = APIRouter()


@router.get("/dashboard", response_model=AdminDashboard)
async def admin_dashboard(db: AsyncSession = Depends(get_db)) -> AdminDashboard:
    service = AdminService(db)
    return await service.get_dashboard()


@router.get("/users/search", response_model=list[AdminUserSearch])
async def search_users(query: SearchUsersQuery, db: AsyncSession = Depends(get_db)) -> list[AdminUserSearch]:
    service = AdminService(db)
    return await service.search_users(query.query, limit=query.page_size, offset=(query.page - 1) * query.page_size)


@router.post("/wallet/adjust")
async def adjust_wallet(adjustment: WalletAdjustment, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    service = AdminService(db)
    await service.adjust_wallet(adjustment.user_id, adjustment.amount, adjustment.reason, UUID(adjustment.admin_id))
    return {"status": "adjusted"}


@router.post("/deposit/{deposit_id}/approve")
async def approve_deposit(deposit_id: UUID, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    service = DepositService(db)
    deposit = await service.approve_deposit(deposit_id, None)
    return {"status": "approved", "transaction_id": str(deposit.transaction_id) if deposit.transaction_id else None}


@router.post("/deposit/{deposit_id}/reject")
async def reject_deposit(deposit_id: UUID, reason: str | None = None, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    service = DepositService(db)
    await service.reject_deposit(deposit_id, reason)
    return {"status": "rejected"}


@router.post("/withdrawal/{withdrawal_id}/approve")
async def approve_withdrawal(withdrawal_id: UUID, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    service = WithdrawalService(db)
    withdrawal = await service.approve_withdrawal(withdrawal_id, None)
    return {"status": "approved", "transaction_id": str(withdrawal.transaction_id) if withdrawal.transaction_id else None}


@router.post("/withdrawal/{withdrawal_id}/reject")
async def reject_withdrawal(withdrawal_id: UUID, reason: str | None = None, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    service = WithdrawalService(db)
    await service.reject_withdrawal(withdrawal_id, reason)
    return {"status": "rejected"}


@router.post("/rooms/{room_id}/control")
async def control_room(room_id: UUID, control: RoomControl, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    service = AdminService(db)
    if control.action == "pause":
        await service.pause_room(room_id)
    elif control.action == "resume":
        await service.resume_room(room_id)
    elif control.action == "stop":
        await service.stop_room(room_id)
    elif control.action == "cancel":
        await service.cancel_room(room_id)
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    return {"status": control.action}


@router.post("/announcements")
async def create_announcement(announcement: AnnouncementCreate, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    service = AdminService(db)
    await service.create_announcement(announcement.title, announcement.body, announcement.priority)
    return {"status": "created"}


@router.get("/audit-logs", response_model=list[AuditLogRead])
async def get_audit_logs(limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_db)) -> list[AuditLogRead]:
    service = AdminService(db)
    return await service.get_audit_logs(limit=limit, offset=offset)


@router.post("/feature-flags")
async def update_feature_flag(flag: FeatureFlagUpdate, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    service = AdminService(db)
    await service.set_feature_flag(flag.key, flag.is_enabled)
    return {"status": "updated"}


@router.post("/maintenance")
async def set_maintenance(mode: MaintenanceModeUpdate, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    service = AdminService(db)
    await service.set_maintenance_mode(mode.is_active, mode.message)
    return {"status": "updated"}


@router.get("/reports/export")
async def export_report(report: ReportExport, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    service = AdminService(db)
    data = await service.generate_report(report.type, report.start_date, report.end_date)
    return {"report": report.type, "data": data}


@router.get("/analytics")
async def get_analytics(period: str = "daily", db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    service = AdminService(db)
    return await service.get_analytics(period)


@router.get("/actions", response_model=list[AdminActionRead])
async def get_admin_actions(limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_db)) -> list[AdminActionRead]:
    service = AdminService(db)
    return await service.get_admin_actions(limit=limit, offset=offset)
