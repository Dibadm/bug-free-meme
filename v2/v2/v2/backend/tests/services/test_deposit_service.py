from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal
from uuid import UUID

from app.services.deposit_service import DepositService
from app.core.exceptions import ValidationError


@pytest.fixture
def mock_db() -> MagicMock:
    db = MagicMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock()
    db.add = AsyncMock()
    db.scalar = AsyncMock()
    return db


class TestDepositService:
    async def test_create_deposit_success(self, mock_db: MagicMock) -> None:
        mock_db.execute.return_value.scalars.return_value.all.return_value = []
        service = DepositService(mock_db)
        result = await service.create_deposit(UUID("00000000-0000-0000-0000-000000000000"), Decimal("100.00"))
        assert result.amount == Decimal("100.00")

    async def test_create_deposit_duplicate_pending(self, mock_db: MagicMock) -> None:
        mock_db.execute.return_value.scalars.return_value.all.return_value = [MagicMock()]
        service = DepositService(mock_db)
        with pytest.raises(ValidationError):
            await service.create_deposit(UUID("00000000-0000-0000-0000-000000000000"), Decimal("100.00"))

    async def test_verify_sms_success(self, mock_db: MagicMock) -> None:
        deposit = MagicMock()
        deposit.id = UUID("00000000-0000-0000-0000-000000000000")
        deposit.status = "pending"
        deposit.sms_verified_at = None
        deposit.user_id = UUID("00000000-0000-0000-0000-000000000000")
        mock_db.execute.return_value.scalar_one_or_none.return_value = deposit
        service = DepositService(mock_db)
        result = await service.verify_sms(deposit.id, "SMS from +251911234567: Payment received")
        assert result.sms_code == "SMS from +251911234567: Payment received"

    async def test_verify_sms_wrong_number(self, mock_db: MagicMock) -> None:
        deposit = MagicMock()
        deposit.id = UUID("00000000-0000-0000-0000-000000000000")
        deposit.status = "pending"
        deposit.sms_verified_at = None
        mock_db.execute.return_value.scalar_one_or_none.return_value = deposit
        service = DepositService(mock_db)
        with pytest.raises(ValidationError):
            await service.verify_sms(deposit.id, "SMS from +251912345678: Payment received")
