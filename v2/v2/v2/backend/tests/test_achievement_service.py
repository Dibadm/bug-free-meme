from __future__ import annotations

import pytest
from uuid import uuid4

from app.models.models import AchievementType
from app.services import AchievementService


@pytest.mark.asyncio
async def test_create_achievement(db_session: Any) -> None:
    service = AchievementService(db_session)
    achievement = await service.create_achievement(
        name="First Win",
        description="Win your first game",
        type=AchievementType.GAMES_PLAYED,
        threshold=1,
        reward_amount=Decimal("10.00"),
    )
    assert achievement.name == "First Win"
    assert achievement.threshold == 1


@pytest.mark.asyncio
async def test_create_achievement_invalid_threshold(db_session: Any) -> None:
    service = AchievementService(db_session)
    with pytest.raises(ValidationError, match="Threshold must be positive"):
        await service.create_achievement(
            name="Bad",
            description="Bad",
            type=AchievementType.GAMES_PLAYED,
            threshold=0,
            reward_amount=Decimal("10.00"),
        )


@pytest.mark.asyncio
async def test_update_progress_completes_achievement(db_session: Any) -> None:
    service = AchievementService(db_session)
    achievement = await service.create_achievement(
        name="Test",
        description="Test",
        type=AchievementType.GAMES_PLAYED,
        threshold=5,
    )
    user_id = uuid4()
    progress = await service.update_progress(user_id, achievement.id, 3)
    assert progress.current_value == 3
    assert not progress.is_completed

    completed = await service.update_progress(user_id, achievement.id, 5)
    assert completed.current_value == 5
    assert completed.is_completed
    assert completed.completed_at is not None
