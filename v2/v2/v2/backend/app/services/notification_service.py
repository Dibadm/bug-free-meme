from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationError
from app.core.logging import get_logger
from app.models.models import Notification, NotificationStatus
from app.repositories import NotificationRepository
from app.services.base import BaseService

logger = get_logger(__name__)


class NotificationService(BaseService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.notification_repo = NotificationRepository(db)

    async def create_notification(self, user_id: UUID, title: str, body: str, notification_type: str, data: dict | None = None, priority: str = "normal") -> Notification:
        if not title or not body:
            raise ValidationError("Title and body are required")
        notification = Notification(
            user_id=user_id,
            title=title,
            body=body,
            type=notification_type,
            data=data,
            priority=priority,
            status=NotificationStatus.PENDING,
        )
        return await self.notification_repo.create(notification)

    async def get_user_notifications(self, user_id: UUID, limit: int = 50, offset: int = 0) -> list[Notification]:
        return await self.notification_repo.get_by_user_id(user_id, limit=limit, offset=offset)

    async def get_unread_notifications(self, user_id: UUID) -> list[Notification]:
        return await self.notification_repo.get_unread_by_user(user_id)

    async def mark_as_read(self, notification_id: UUID) -> Notification | None:
        notification = await self.notification_repo.get_by_id(notification_id)
        if not notification:
            return None
        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(notification)
        return notification

    async def mark_all_as_read(self, user_id: UUID) -> None:
        notifications = await self.notification_repo.get_unread_by_user(user_id)
        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.now(timezone.utc)
        await self.db.flush()

    async def get_pending_notifications(self, limit: int = 50) -> list[Notification]:
        return await self.notification_repo.get_pending(limit=limit)

    async def deliver(self, notification_id: UUID) -> bool:
        notification = await self.notification_repo.get_by_id(notification_id)
        if not notification:
            return False
        try:
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.now(timezone.utc)
            await self.db.flush()
            await self.db.refresh(notification)
            return True
        except Exception as exc:
            notification.status = NotificationStatus.FAILED
            notification.retry_count = (notification.retry_count or 0) + 1
            await self.db.flush()
            logger.error("notification_delivery_failed", notification_id=str(notification_id), error=str(exc))
            return False

    async def schedule_notification(self, user_id: UUID, title: str, body: str, notification_type: str, scheduled_at: datetime, data: dict | None = None) -> Notification:
        notification = Notification(
            user_id=user_id,
            title=title,
            body=body,
            type=notification_type,
            data=data,
            status=NotificationStatus.SCHEDULED,
            scheduled_at=scheduled_at,
        )
        return await self.notification_repo.create(notification)

    async def send_immediate(self, user_id: UUID, title: str, body: str, notification_type: str, data: dict | None = None) -> Notification:
        return await self.create_notification(user_id, title, body, notification_type, data=data, priority="high")

    async def send_silent(self, user_id: UUID, title: str, body: str, notification_type: str, data: dict | None = None) -> Notification:
        return await self.create_notification(user_id, title, body, notification_type, data=data, priority="silent")
