from __future__ import annotations

import pytest
from uuid import uuid4

from app.core.exceptions import ValidationError
from app.models.models import RoomStatus, GameStatus
from app.services import RoomService


@pytest.mark.asyncio
async def test_create_room(db_session: Any) -> None:
    from app.services import RoomTemplateService

    template_service = RoomTemplateService(db_session)
    template = await template_service.create_template(
        name="Template",
        entry_fee=10.0,
        max_players=10,
        min_players=2,
        winning_pattern="four_corners",
        house_percentage=Decimal("60.00"),
    )

    room_service = RoomService(db_session)
    room = await room_service.create_room(template.id, "Room 1")
    assert room.name == "Room 1"
    assert room.status == RoomStatus.WAITING


@pytest.mark.asyncio
async def test_room_lifecycle(db_session: Any) -> None:
    from app.services import RoomTemplateService

    template_service = RoomTemplateService(db_session)
    template = await template_service.create_template(
        name="Template",
        entry_fee=10.0,
        max_players=10,
        min_players=2,
        winning_pattern="four_corners",
        house_percentage=Decimal("60.00"),
    )

    room_service = RoomService(db_session)
    room = await room_service.create_room(template.id, "Room 1")
    assert room.status == RoomStatus.WAITING

    opened = await room_service.open_room(room.id)
    assert opened.status == RoomStatus.OPEN

    locked = await room_service.lock_room(room.id)
    assert locked.status == RoomStatus.LOCKED

    game = await room_service.start_game(room.id)
    assert game.status == GameStatus.RUNNING
    assert room.status == RoomStatus.RUNNING

    finished = await room_service.finish_game(room.id)
    assert finished.status == RoomStatus.FINISHED


@pytest.mark.asyncio
async def test_start_game_invalid_state(db_session: Any) -> None:
    from app.services import RoomTemplateService

    template_service = RoomTemplateService(db_session)
    template = await template_service.create_template(
        name="Template",
        entry_fee=10.0,
        max_players=10,
        min_players=2,
        winning_pattern="four_corners",
        house_percentage=Decimal("60.00"),
    )

    room_service = RoomService(db_session)
    room = await room_service.create_room(template.id, "Room 1")
    await room_service.open_room(room.id)

    with pytest.raises(ValidationError, match="must be locked"):
        await room_service.start_game(room.id)
