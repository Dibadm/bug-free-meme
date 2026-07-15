from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.notification_service import NotificationService
from app.repositories.notification_repository import NotificationRepository


@pytest.fixture
def mock_db() -> MagicMock:
    db = MagicMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock()
    db.add = AsyncMock()
    return db


class TestNotificationRepository:
    async def test_get_pending(self, mock_db: MagicMock) -> None:
        mock_db.execute.return_value.scalars.return_value.all.return_value = []
        repo = NotificationRepository(mock_db)
        result = await repo.get_pending()
        assert result == []

    async def test_get_failed_notifications(self, mock_db: MagicMock) -> None:
        mock_db.execute.return_value.scalars.return_value.all.return_value = []
        repo = NotificationRepository(mock_db)
        result = await repo.get_failed_notifications()
        assert result == []

    async def test_update_status(self, mock_db: MagicMock) -> None:
        notification = MagicMock()
        mock_db.execute.return_value.scalar_one_or_none.return_value = notification
        repo = NotificationRepository(mock_db)
        await repo.update_status("notif-1", "sent")
        assert notification.status.value == "sent"


class TestNotificationService:
    async def test_create_notification(self, mock_db: MagicMock) -> None:
        service = NotificationService(mock_db)
        result = await service.create_notification("user-1", "Title", "Body", "system")
        assert result.title == "Title"

    async def test_schedule_notification(self, mock_db: MagicMock) -> None:
        service = NotificationService(mock_db)
        result = await service.schedule_notification("user-1", "Title", "Body", "system", None)
        assert result.title == "Title"

    async def test_send_immediate(self, mock_db: MagicMock) -> None:
        service = NotificationService(mock_db)
        result = await service.send_immediate("user-1", "Title", "Body", "system")
        assert result.priority == "high"

    async def test_send_silent(self, mock_db: MagicMock) -> None:
        service = NotificationService(mock_db)
        result = await service.send_silent("user-1", "Title", "Body", "system")
        assert result.priority == "silent"
