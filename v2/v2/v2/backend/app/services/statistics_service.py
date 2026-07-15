from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

from app.models.models import PlayerStatistics
from app.repositories import StatisticsRepository
from app.services.base import BaseService


class StatisticsService(BaseService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.stats_repo = StatisticsRepository(db)

    async def get_stats(self, user_id: UUID) -> PlayerStatistics | None:
        return await self.stats_repo.get_by_user_id(user_id)

    async def record_game_played(self, user_id: UUID, won: bool) -> PlayerStatistics:
        stats = await self.stats_repo.get_by_user_id(user_id)
        if not stats:
            stats = PlayerStatistics(user_id=user_id)
            await self.stats_repo.create(stats)

        stats.games_played += 1
        if won:
            stats.games_won += 1
            stats.current_streak += 1
            stats.best_streak = max(stats.best_streak, stats.current_streak)
        else:
            stats.current_streak = 0

        stats.win_rate = Decimal(str(round((stats.games_won / stats.games_played) * 100, 2)))
        await self.db.flush()
        await self.db.refresh(stats)
        return stats

    async def record_card_purchased(self, user_id: UUID) -> PlayerStatistics:
        stats = await self.stats_repo.get_by_user_id(user_id)
        if not stats:
            stats = PlayerStatistics(user_id=user_id)
            await self.stats_repo.create(stats)

        stats.cards_purchased += 1
        await self.db.flush()
        await self.db.refresh(stats)
        return stats

    async def record_deposit(self, user_id: UUID, amount: Decimal) -> PlayerStatistics:
        stats = await self.stats_repo.get_by_user_id(user_id)
        if not stats:
            stats = PlayerStatistics(user_id=user_id)
            await self.stats_repo.create(stats)

        stats.total_deposited = (stats.total_deposited or Decimal("0.00")) + amount
        await self.db.flush()
        await self.db.refresh(stats)
        return stats

    async def record_withdrawal(self, user_id: UUID, amount: Decimal) -> PlayerStatistics:
        stats = await self.stats_repo.get_by_user_id(user_id)
        if not stats:
            stats = PlayerStatistics(user_id=user_id)
            await self.stats_repo.create(stats)

        stats.total_withdrawn = (stats.total_withdrawn or Decimal("0.00")) + amount
        await self.db.flush()
        await self.db.refresh(stats)
        return stats

    async def record_win(self, user_id: UUID, amount: Decimal) -> PlayerStatistics:
        stats = await self.stats_repo.get_by_user_id(user_id)
        if not stats:
            stats = PlayerStatistics(user_id=user_id)
            await self.stats_repo.create(stats)

        stats.total_won = (stats.total_won or Decimal("0.00")) + amount
        await self.db.flush()
        await self.db.refresh(stats)
        return stats
