from __future__ import annotations

import pytest
from decimal import Decimal
from uuid import uuid4

from app.services import StatisticsService


@pytest.mark.asyncio
async def test_record_game_played(db_session: Any) -> None:
    service = StatisticsService(db_session)
    user_id = uuid4()

    stats = await service.record_game_played(user_id, won=False)
    assert stats.games_played == 1
    assert stats.games_won == 0
    assert stats.current_streak == 0

    stats = await service.record_game_played(user_id, won=True)
    assert stats.games_played == 2
    assert stats.games_won == 1
    assert stats.current_streak == 1
    assert stats.best_streak == 1


@pytest.mark.asyncio
async def test_record_game_loses_streak(db_session: Any) -> None:
    service = StatisticsService(db_session)
    user_id = uuid4()
    await service.record_game_played(user_id, won=True)
    await service.record_game_played(user_id, won=True)
    await service.record_game_played(user_id, won=False)

    stats = await service.record_game_played(user_id, won=False)
    assert stats.current_streak == 0
    assert stats.best_streak == 2
    assert stats.win_rate == Decimal("50.00")


@pytest.mark.asyncio
async def test_record_financials(db_session: Any) -> None:
    service = StatisticsService(db_session)
    user_id = uuid4()

    await service.record_deposit(user_id, Decimal("100.00"))
    await service.record_withdrawal(user_id, Decimal("50.00"))
    await service.record_win(user_id, Decimal("200.00"))

    stats = await service.get_stats(user_id)
    assert stats.total_deposited == Decimal("100.00")
    assert stats.total_withdrawn == Decimal("50.00")
    assert stats.total_won == Decimal("200.00")
