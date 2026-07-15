from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.admin_service import AdminService
from app.services.notification_service import NotificationService


@pytest.fixture
def mock_db() -> MagicMock:
    db = MagicMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock()
    db.scalar = AsyncMock()
    db.add = AsyncMock()
    return db


class TestAdminService:
    async def test_search_users(self, mock_db: MagicMock) -> None:
        mock_db.execute.return_value.scalars.return_value.all.return_value = []
        service = AdminService(mock_db)
        result = await service.search_users("test")
        assert result == []

    async def test_get_dashboard(self, mock_db: MagicMock) -> None:
        mock_db.scalar.side_effect = [100.0, 1000.0, 5, 2, 5000.0]
        service = AdminService(mock_db)
        result = await service.get_dashboard()
        assert "revenue_today" in result
        assert "revenue_month" in result

    async def test_toggle_maintenance(self, mock_db: MagicMock) -> None:
        mock_db.execute.return_value.scalar_one.return_value = None
        service = AdminService(mock_db)
        result = await service.toggle_maintenance(True, "Upgrade")
        assert result.is_active is True

    async def test_create_announcement(self, mock_db: MagicMock) -> None:
        service = AdminService(mock_db)
        result = await service.create_announcement("Title", "Body", 1)
        assert result.title == "Title"

    async def test_set_feature_flag(self, mock_db: MagicMock) -> None:
        service = AdminService(mock_db)
        result = await service.set_feature_flag("new_feature", True)
        assert result.is_enabled is True


class TestNotificationService:
    async def test_create_notification(self, mock_db: MagicMock) -> None:
        mock_db.execute.return_value.scalars.return_value.all.return_value = []
        service = NotificationService(mock_db)
        result = await service.create_notification("user-1", "Title", "Body", "system")
        assert result.title == "Title"

    async def test_get_user_notifications(self, mock_db: MagicMock) -> None:
        mock_db.execute.return_value.scalars.return_value.all.return_value = []
        service = NotificationService(mock_db)
        result = await service.get_user_notifications("user-1")
        assert result == []

    async def test_get_unread_notifications(self, mock_db: MagicMock) -> None:
        mock_db.execute.return_value.scalars.return_value.all.return_value = []
        service = NotificationService(mock_db)
        result = await service.get_unread_notifications("user-1")
        assert result == []

    async def test_mark_as_read(self, mock_db: MagicMock) -> None:
        notification = MagicMock()
        notification.id = "notif-1"
        mock_db.execute.return_value.scalar_one_or_none.return_value = notification
        service = NotificationService(mock_db)
        result = await service.mark_as_read("notif-1")
        assert result.is_read is True
