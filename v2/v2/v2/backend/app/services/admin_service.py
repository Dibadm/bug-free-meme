from __future__ import annotations

from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID

from app.core.exceptions import ValidationError
from app.models.models import (
    AdminAction,
    AuditLog,
    MaintenanceMode,
    Room,
    RoomStatus,
    User,
    Wallet,
    WalletTransaction,
    WalletTransactionType,
)
from app.repositories import (
    AdminActionRepository,
    AuditRepository,
    MaintenanceModeRepository,
    RoomRepository,
    UserRepository,
    WalletRepository,
)
from app.services.base import BaseService
from sqlalchemy import select, func, or_, desc
from sqlalchemy.sql import Select
from sqlalchemy.ext.asyncio import AsyncSession


class AdminService(BaseService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.user_repo = UserRepository(db)
        self.wallet_repo = WalletRepository(db)
        self.audit_repo = AuditRepository(db)
        self.maintenance_repo = MaintenanceModeRepository(db)
        self.admin_action_repo = AdminActionRepository(db)
        self.room_repo = RoomRepository(db)

    async def search_users(self, query: str, limit: int = 20, offset: int = 0) -> list[User]:
        pattern = f"%{query}%"
        result = await self.db.execute(
            select(User)
            .where(
                User.deleted_at.is_(None),
                or_(
                    User.username.ilike(pattern),
                    User.first_name.ilike(pattern),
                    User.last_name.ilike(pattern),
                    User.telegram_id.cast(str).ilike(pattern),
                ),
            )
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def adjust_wallet(self, user_id: UUID, amount: Decimal, reason: str, performed_by: UUID) -> WalletTransaction:
        from app.services.wallet_service import WalletService
        wallet_service = WalletService(self.db)
        if amount > 0:
            return await wallet_service.credit(
                user_id,
                amount,
                WalletTransactionType.ADJUSTMENT,
                description=f"Admin adjustment: {reason}",
            )
        debit_amount = abs(amount)
        return await wallet_service.debit(
            user_id,
            debit_amount,
            WalletTransactionType.ADJUSTMENT,
            description=f"Admin adjustment: {reason}",
        )

    async def toggle_maintenance(self, is_active: bool, message: str | None = None) -> Any:
        current = await self.maintenance_repo.get_current()
        if current:
            current.is_active = is_active
            current.message = message
            current.started_at = datetime.now(timezone.utc) if is_active else None
            current.ended_at = datetime.now(timezone.utc) if not is_active else None
            await self.db.flush()
            await self.db.refresh(current)
            return current

        mode = MaintenanceMode(is_active=is_active, message=message, started_at=datetime.now(timezone.utc) if is_active else None)
        return await self.maintenance_repo.create(mode)

    async def get_dashboard(self) -> dict[str, Any]:
        today = datetime.now(timezone.utc).date()
        month_start = today.replace(day=1)

        revenue_today = await self.db.scalar(
            select(func.coalesce(func.sum(WalletTransaction.amount), 0)).where(
                WalletTransaction.type == WalletTransactionType.DEPOSIT,
                WalletTransaction.status == "completed",
                func.date(WalletTransaction.created_at) == today,
            )
        )
        revenue_month = await self.db.scalar(
            select(func.coalesce(func.sum(WalletTransaction.amount), 0)).where(
                WalletTransaction.type == WalletTransactionType.DEPOSIT,
                WalletTransaction.status == "completed",
                func.date(WalletTransaction.created_at) >= month_start,
            )
        )
        active_games = await self.db.scalar(select(func.count(Room.id)).where(Room.status == RoomStatus.RUNNING))
        pending_withdrawals = await self.db.scalar(
            select(func.count(WalletTransaction.id)).where(
                WalletTransaction.type == WalletTransactionType.WITHDRAWAL,
                WalletTransaction.status == "pending",
            )
        )
        house_wallet = await self.db.scalar(select(Wallet).where(Wallet.user_id == UUID("00000000-0000-0000-0000-000000000000")))
        house_balance = house_wallet.balance if house_wallet else Decimal("0.00")

        return {
            "revenue_today": revenue_today or Decimal("0.00"),
            "revenue_month": revenue_month or Decimal("0.00"),
            "active_games": active_games or 0,
            "pending_withdrawals": pending_withdrawals or 0,
            "house_balance": house_balance,
        }

    async def pause_room(self, room_id: UUID) -> None:
        room = await self.room_repo.get_by_id(room_id)
        if not room:
            raise ValidationError("Room not found")
        if room.status != RoomStatus.RUNNING:
            raise ValidationError("Room is not running")
        room.status = RoomStatus.PAUSED
        await self.db.flush()

    async def resume_room(self, room_id: UUID) -> None:
        room = await self.room_repo.get_by_id(room_id)
        if not room:
            raise ValidationError("Room not found")
        if room.status != RoomStatus.PAUSED:
            raise ValidationError("Room is not paused")
        room.status = RoomStatus.RUNNING
        await self.db.flush()

    async def stop_room(self, room_id: UUID) -> None:
        room = await self.room_repo.get_by_id(room_id)
        if not room:
            raise ValidationError("Room not found")
        room.status = RoomStatus.FINISHED
        await self.db.flush()

    async def cancel_room(self, room_id: UUID) -> None:
        room = await self.room_repo.get_by_id(room_id)
        if not room:
            raise ValidationError("Room not found")
        room.status = RoomStatus.CANCELLED
        await self.db.flush()

    async def create_announcement(self, title: str, body: str, priority: int = 0) -> Any:
        from app.models.models import Announcement
        announcement = Announcement(title=title, body=body, priority=priority, published_at=datetime.now(timezone.utc))
        await self.db.add(announcement)
        await self.db.flush()
        await self.db.refresh(announcement)
        return announcement

    async def set_feature_flag(self, key: str, is_enabled: bool) -> Any:
        from app.repositories import FeatureFlagRepository
        flag_repo = FeatureFlagRepository(self.db)
        flag = await flag_repo.get_by_key(key)
        if flag:
            flag.is_enabled = is_enabled
            await self.db.flush()
            await self.db.refresh(flag)
            return flag
        from app.models.models import FeatureFlag
        flag = FeatureFlag(key=key, is_enabled=is_enabled)
        return await flag_repo.create(flag)

    async def set_maintenance_mode(self, is_active: bool, message: str | None = None) -> Any:
        return await self.toggle_maintenance(is_active, message)

    async def get_audit_logs(self, limit: int = 100, offset: int = 0) -> list[AuditLog]:
        result = await self.db.execute(
            select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def get_admin_actions(self, limit: int = 100, offset: int = 0) -> list[AdminAction]:
        result = await self.db.execute(
            select(AdminAction).order_by(AdminAction.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def generate_report(self, report_type: str, start_date: datetime, end_date: datetime) -> dict[str, Any]:
        if report_type == "revenue":
            total = await self.db.scalar(
                select(func.coalesce(func.sum(WalletTransaction.amount), 0)).where(
                    WalletTransaction.type == WalletTransactionType.DEPOSIT,
                    WalletTransaction.status == "completed",
                    WalletTransaction.created_at >= start_date,
                    WalletTransaction.created_at <= end_date,
                )
            )
            return {"total_revenue": total or Decimal("0.00"), "period": {"start": start_date.isoformat(), "end": end_date.isoformat()}}
        if report_type == "users":
            total_users = await self.db.scalar(select(func.count(User.id)).where(User.deleted_at.is_(None)))
            new_users = await self.db.scalar(
                select(func.count(User.id)).where(
                    User.created_at >= start_date,
                    User.created_at <= end_date,
                    User.deleted_at.is_(None),
                )
            )
            return {"total_users": total_users or 0, "new_users": new_users or 0}
        if report_type == "games":
            total_games = await self.db.scalar(select(func.count(Game.id)).where(Game.created_at >= start_date, Game.created_at <= end_date))
            finished_games = await self.db.scalar(
                select(func.count(Game.id)).where(
                    Game.status == "finished",
                    Game.created_at >= start_date,
                    Game.created_at <= end_date,
                )
            )
            return {"total_games": total_games or 0, "finished_games": finished_games or 0}
        return {"error": "Unknown report type"}

    async def get_analytics(self, period: str = "daily") -> dict[str, Any]:
        if period == "daily":
            today = datetime.now(timezone.utc).date()
            active_users = await self.db.scalar(
                select(func.count(func.distinct(User.id))).where(User.last_seen >= today, User.deleted_at.is_(None))
            )
            games_played = await self.db.scalar(
                select(func.count(Game.id)).where(Game.created_at >= today, Game.status == "finished")
            )
            return {"active_users": active_users or 0, "games_played": games_played or 0, "period": period}
        if period == "weekly":
            week_start = datetime.now(timezone.utc).date() - datetime.timedelta(days=7)
            active_users = await self.db.scalar(
                select(func.count(func.distinct(User.id))).where(User.last_seen >= week_start, User.deleted_at.is_(None))
            )
            games_played = await self.db.scalar(
                select(func.count(Game.id)).where(Game.created_at >= week_start, Game.status == "finished")
            )
            return {"active_users": active_users or 0, "games_played": games_played or 0, "period": period}
        return {"period": period}
