from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal
from uuid import UUID

from app.services.payment_settings_service import PaymentSettingsService
from app.models.models import PaymentSettings


@pytest.fixture
def mock_db() -> MagicMock:
    db = MagicMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock()
    db.add = AsyncMock()
    db.scalar = AsyncMock()
    return db


@pytest.fixture
def mock_audit_service() -> MagicMock:
    service = MagicMock()
    service.log = AsyncMock()
    return service


class TestPaymentSettingsService:
    async def test_get_or_create_default_creates_new(self, mock_db: MagicMock) -> None:
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        service = PaymentSettingsService(mock_db)
        result = await service.get_or_create_default()
        assert result.telebirr_number == ""
        assert result.is_deposit_enabled is True

    async def test_validate_settings_success(self, mock_db: MagicMock) -> None:
        service = PaymentSettingsService(mock_db)
        service.validate_settings({
            "telebirr_number": "+251911234567",
            "min_deposit": Decimal("10.00"),
            "max_deposit": Decimal("1000.00"),
        })

    async def test_validate_settings_invalid_phone(self, mock_db: MagicMock) -> None:
        service = PaymentSettingsService(mock_db)
        with pytest.raises(Exception):
            service.validate_settings({
                "telebirr_number": "0911234567",
                "min_deposit": Decimal("10.00"),
                "max_deposit": Decimal("1000.00"),
            })

    async def test_validate_settings_max_less_than_min(self, mock_db: MagicMock) -> None:
        service = PaymentSettingsService(mock_db)
        with pytest.raises(Exception):
            service.validate_settings({
                "telebirr_number": "+251911234567",
                "min_deposit": Decimal("100.00"),
                "max_deposit": Decimal("10.00"),
            })
