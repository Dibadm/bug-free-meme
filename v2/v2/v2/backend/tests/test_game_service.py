from __future__ import annotations

import pytest
from uuid import uuid4

from app.core.exceptions import ValidationError
from app.models.models import GameStatus
from app.services import GameService


@pytest.mark.asyncio
async def test_pause_and_resume_game(db_session: Any) -> None:
    from app.services import RoomTemplateService, RoomService

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
    await room_service.lock_room(room.id)
    game = await room_service.start_game(room.id)

    game_service = GameService(db_session)
    paused = await game_service.pause_game(game.id)
    assert paused.status == GameStatus.PAUSED

    resumed = await game_service.resume_game(game.id)
    assert resumed.status == GameStatus.RUNNING


@pytest.mark.asyncio
async def test_cancel_game(db_session: Any) -> None:
    from app.services import RoomTemplateService, RoomService

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
    await room_service.lock_room(room.id)
    game = await room_service.start_game(room.id)

    game_service = GameService(db_session)
    cancelled = await game_service.cancel_game(game.id)
    assert cancelled.status == GameStatus.CANCELLED
    assert cancelled.finished_at is not None


@pytest.mark.asyncio
async def test_finish_game_prevents_double_finish(db_session: Any) -> None:
    from app.services import RoomTemplateService, RoomService

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
    await room_service.lock_room(room.id)
    game = await room_service.start_game(room.id)

    game_service = GameService(db_session)
    await game_service.finish_game(game.id, winner_id=uuid4(), winning_pattern="four_corners", prize_amount=Decimal("100.00"))
    with pytest.raises(ValidationError, match="already finished"):
        await game_service.finish_game(game.id, winner_id=uuid4(), winning_pattern="four_corners", prize_amount=Decimal("100.00"))
