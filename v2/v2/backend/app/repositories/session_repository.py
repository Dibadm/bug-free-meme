from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select, func

from app.models.models import Session
from app.repositories.base_repository import BaseRepository


class SessionRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, Session)

    async def get_by_token_hash(self, token_hash: str) -> Session | None:
        result = await self.db.execute(
            select(Session).where(Session.token_hash == token_hash, Session.revoked_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_active_sessions_by_user(self, user_id: UUID) -> list[Session]:
        result = await self.db.execute(
            select(Session)
            .where(Session.user_id == user_id, Session.revoked_at.is_(None), Session.expires_at > datetime.now(timezone.utc))
            .order_by(Session.last_used_at.desc())
        )
        return list(result.scalars().all())

    async def revoke_session(self, session_id: UUID) -> Session | None:
        session = await self.get_by_id(session_id)
        if session and not session.revoked_at:
            session.revoked_at = datetime.now(timezone.utc)
            await self.db.flush()
            await self.db.refresh(session)
        return session

    async def revoke_all_user_sessions(self, user_id: UUID) -> None:
        result = await self.db.execute(
            select(Session).where(Session.user_id == user_id, Session.revoked_at.is_(None))
        )
        sessions = result.scalars().all()
        now = datetime.now(timezone.utc)
        for session in sessions:
            session.revoked_at = now
        await self.db.flush()

    async def cleanup_expired_sessions(self) -> None:
        result = await self.db.execute(
            select(Session).where(Session.expires_at < datetime.now(timezone.utc), Session.revoked_at.is_(None))
        )
        sessions = result.scalars().all()
        now = datetime.now(timezone.utc)
        for session in sessions:
            session.revoked_at = now
        await self.db.flush()
