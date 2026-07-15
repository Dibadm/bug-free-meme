from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.repositories.payment_settings_repository import PaymentSettingsRepository
from app.models.models import PaymentSettings


@pytest.fixture
def mock_db() -> MagicMock:
    db = MagicMock()
    db.execute = AsyncMock()
    return db


class TestPaymentSettingsRepository:
    async def test_get_active(self, mock_db: MagicMock) -> None:
        settings = PaymentSettings(
            telebirr_number="+251911234567",
            account_holder_name="Test",
            deposit_instructions="Test",
            min_deposit=10.0,
            max_deposit=1000.0,
        )
        mock_db.execute.return_value.scalar_one_or_none.return_value = settings
        repo = PaymentSettingsRepository(mock_db)
        result = await repo.get_active()
        assert result.telebirr_number == "+251911234567"

    async def test_get_all(self, mock_db: MagicMock) -> None:
        mock_db.execute.return_value.scalars.return_value.all.return_value = []
        repo = PaymentSettingsRepository(mock_db)
        result = await repo.get_all()
        assert result == []
