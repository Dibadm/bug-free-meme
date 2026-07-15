from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from app.core.logging import get_logger
from app.services.notification_service import NotificationService

logger = get_logger(__name__)


class NotificationWorker:
    def __init__(self, db_factory: Any) -> None:
        self.db_factory = db_factory
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run(self) -> None:
        while self._running:
            try:
                await asyncio.sleep(5)
                await self._process_queue()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("notification_worker_error", error=str(exc))

    async def _process_queue(self) -> None:
        async with self.db_factory() as db:
            service = NotificationService(db)
            pending = await service.get_pending_notifications(limit=50)
            for notification in pending:
                try:
                    await service.deliver(notification.id)
                except Exception as exc:
                    logger.error("notification_delivery_error", notification_id=str(notification.id), error=str(exc))


class ReminderWorker:
    def __init__(self, db_factory: Any) -> None:
        self.db_factory = db_factory
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run(self) -> None:
        while self._running:
            try:
                await asyncio.sleep(60)
                await self._send_reminders()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("reminder_worker_error", error=str(exc))

    async def _send_reminders(self) -> None:
        async with self.db_factory() as db:
            from app.services import ReferralService
            referral_service = ReferralService(db)
            await referral_service.send_inactive_referral_reminders()


class GameSchedulerWorker:
    def __init__(self, db_factory: Any) -> None:
        self.db_factory = db_factory
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run(self) -> None:
        while self._running:
            try:
                await asyncio.sleep(30)
                await self._schedule_games()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("game_scheduler_error", error=str(exc))

    async def _schedule_games(self) -> None:
        async with self.db_factory() as db:
            from app.services import RoomService
            room_service = RoomService(db)
            await room_service.schedule_pending_rooms()


class CleanupWorker:
    def __init__(self, db_factory: Any) -> None:
        self.db_factory = db_factory
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run(self) -> None:
        while self._running:
            try:
                await asyncio.sleep(3600)
                await self._cleanup()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("cleanup_worker_error", error=str(exc))

    async def _cleanup(self) -> None:
        async with self.db_factory() as db:
            from app.repositories import SessionRepository
            session_repo = SessionRepository(db)
            await session_repo.delete_expired_sessions()
            from app.repositories import RoomRepository
            room_repo = RoomRepository(db)
            await room_repo.delete_expired_rooms()


class LeaderboardRefreshWorker:
    def __init__(self, db_factory: Any) -> None:
        self.db_factory = db_factory
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run(self) -> None:
        while self._running:
            try:
                await asyncio.sleep(3600)
                await self._refresh()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("leaderboard_refresh_error", error=str(exc))

    async def _refresh(self) -> None:
        async with self.db_factory() as db:
            from app.services import LeaderboardService
            service = LeaderboardService(db)
            await service.refresh_weekly_leaderboard()
            await service.refresh_monthly_leaderboard()


class StatisticsAggregationWorker:
    def __init__(self, db_factory: Any) -> None:
        self.db_factory = db_factory
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run(self) -> None:
        while self._running:
            try:
                await asyncio.sleep(1800)
                await self._aggregate()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("statistics_aggregation_error", error=str(exc))

    async def _aggregate(self) -> None:
        async with self.db_factory() as db:
            from app.services import StatisticsService
            service = StatisticsService(db)
            await service.aggregate_daily()


class AuditArchivingWorker:
    def __init__(self, db_factory: Any) -> None:
        self.db_factory = db_factory
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run(self) -> None:
        while self._running:
            try:
                await asyncio.sleep(86400)
                await self._archive()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("audit_archiving_error", error=str(exc))

    async def _archive(self) -> None:
        async with self.db_factory() as db:
            cutoff = datetime.now(timezone.utc).replace(day=1)
            from app.repositories import AuditRepository
            audit_repo = AuditRepository(db)
            await audit_repo.archive_before(cutoff)


class RetryQueueWorker:
    def __init__(self, db_factory: Any) -> None:
        self.db_factory = db_factory
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run(self) -> None:
        while self._running:
            try:
                await asyncio.sleep(10)
                await self._retry()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("retry_queue_error", error=str(exc))

    async def _retry(self) -> None:
        async with self.db_factory() as db:
            from app.repositories import NotificationRepository
            repo = NotificationRepository(db)
            failed = await repo.get_failed_notifications(limit=50)
            for notification in failed:
                try:
                    await repo.update_status(notification.id, "pending")
                except Exception as exc:
                    logger.error("retry_queue_update_error", notification_id=str(notification.id), error=str(exc))


class HealthMonitorWorker:
    def __init__(self, db_factory: Any, ws_manager: Any) -> None:
        self.db_factory = db_factory
        self.ws_manager = ws_manager
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run(self) -> None:
        while self._running:
            try:
                await asyncio.sleep(30)
                await self._check()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("health_monitor_error", error=str(exc))

    async def _check(self) -> None:
        stats = self.ws_manager.get_stats()
        logger.info("health_monitor_stats", **stats)
        if stats.get("total_connections", 0) > 10000:
            logger.warning("high_connection_count", connections=stats.get("total_connections"))
