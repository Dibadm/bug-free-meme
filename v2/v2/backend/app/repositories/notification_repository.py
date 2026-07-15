from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, func

from app.models.models import Notification, NotificationStatus
from app.repositories.base_repository import BaseRepository


class NotificationRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, Notification)

    async def get_by_user_id(self, user_id: Any, limit: int = 50, offset: int = 0) -> list[Notification]:
        result = await self.db.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_unread_by_user(self, user_id: Any) -> list[Notification]:
        result = await self.db.execute(
            select(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
            .order_by(Notification.created_at.desc())
        )
        return list(result.scalars().all())

    async def count_unread(self, user_id: Any) -> int:
        result = await self.db.execute(
            select(func.count()).where(Notification.user_id == user_id, Notification.is_read == False)
        )
        return result.scalar_one() or 0

    async def get_pending(self, limit: int = 50) -> list[Notification]:
        result = await self.db.execute(
            select(Notification)
            .where(Notification.status == NotificationStatus.PENDING)
            .order_by(Notification.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_failed_notifications(self, limit: int = 50) -> list[Notification]:
        result = await self.db.execute(
            select(Notification)
            .where(Notification.status == NotificationStatus.FAILED)
            .order_by(Notification.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_status(self, notification_id: Any, status: str) -> None:
        notification = await self.get_by_id(notification_id)
        if not notification:
            return
        notification.status = NotificationStatus(status)
        if status == "SENT":
            notification.sent_at = datetime.now(timezone.utc)
        await self.db.flush()
