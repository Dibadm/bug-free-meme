from __future__ import annotations

from typing import Any
from uuid import UUID

from app.models.models import AuditLog
from app.repositories import AuditRepository
from app.services.base import BaseService


class AuditService(BaseService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.audit_repo = AuditRepository(db)

    async def log(
        self,
        actor_id: UUID | None,
        action: str,
        entity_type: str | None = None,
        entity_id: Any = None,
        old_value: dict | None = None,
        new_value: dict | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuditLog:
        log_entry = AuditLog(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return await self.audit_repo.create(log_entry)

    async def get_actor_logs(self, actor_id: UUID, limit: int = 100, offset: int = 0) -> list[AuditLog]:
        return await self.audit_repo.get_by_actor_id(actor_id, limit=limit, offset=offset)

    async def get_entity_logs(self, entity_type: str, entity_id: Any) -> list[AuditLog]:
        return await self.audit_repo.get_by_entity(entity_type, entity_id)

    async def get_recent_logs(self, limit: int = 100) -> list[AuditLog]:
        return await self.audit_repo.get_recent(limit=limit)
