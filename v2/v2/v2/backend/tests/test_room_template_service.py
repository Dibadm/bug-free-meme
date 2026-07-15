from __future__ import annotations

import pytest
from decimal import Decimal
from uuid import uuid4

from app.core.exceptions import ValidationError
from app.models.models import RoomStatus
from app.services import RoomTemplateService


@pytest.mark.asyncio
async def test_create_room_template(db_session: Any) -> None:
    service = RoomTemplateService(db_session)
    template = await service.create_template(
        name="Test Room",
        entry_fee=Decimal("10.00"),
        max_players=50,
        min_players=2,
        winning_pattern="four_corners",
        house_percentage=Decimal("60.00"),
        referral_percentage=Decimal("10.00"),
        bonus_percentage=Decimal("10.00"),
        jackpot_percentage=Decimal("10.00"),
    )
    assert template.name == "Test Room"
    assert template.status == RoomStatus.DRAFT


@pytest.mark.asyncio
async def test_create_template_invalid_min_players(db_session: Any) -> None:
    service = RoomTemplateService(db_session)
    with pytest.raises(ValidationError, match="Minimum players"):
        await service.create_template(
            name="Bad Room",
            entry_fee=Decimal("10.00"),
            max_players=10,
            min_players=0,
            winning_pattern="four_corners",
            house_percentage=Decimal("60.00"),
        )


@pytest.mark.asyncio
async def test_create_template_exceeds_100_percent(db_session: Any) -> None:
    service = RoomTemplateService(db_session)
    with pytest.raises(ValidationError, match="cannot exceed 100%"):
        await service.create_template(
            name="Bad Room",
            entry_fee=Decimal("10.00"),
            max_players=10,
            min_players=2,
            winning_pattern="four_corners",
            house_percentage=Decimal("80.00"),
            referral_percentage=Decimal("30.00"),
        )


@pytest.mark.asyncio
async def test_activate_template(db_session: Any) -> None:
    service = RoomTemplateService(db_session)
    template = await service.create_template(
        name="Active Room",
        entry_fee=Decimal("10.00"),
        max_players=50,
        min_players=2,
        winning_pattern="four_corners",
        house_percentage=Decimal("60.00"),
    )
    activated = await service.activate_template(template.id)
    assert activated.status == RoomStatus.ACTIVE
