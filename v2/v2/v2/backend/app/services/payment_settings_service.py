from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from app.core.exceptions import ValidationError
from app.models.models import PaymentSettings
from app.repositories import PaymentSettingsRepository
from app.services.audit_service import AuditService
from app.services.base import BaseService
from app.websocket.channels import AdminChannel
from app.websocket.events import EventType
from sqlalchemy.ext.asyncio import AsyncSession


class PaymentSettingsService(BaseService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.payment_repo = PaymentSettingsRepository(db)
        self.audit_service = AuditService(db)

    async def get_active_settings(self) -> PaymentSettings | None:
        return await self.payment_repo.get_active()

    async def get_all_settings(self) -> list[PaymentSettings]:
        return await self.payment_repo.get_all()

    async def update_settings(
        self,
        settings_id: UUID,
        updates: dict[str, Any],
        actor_id: UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> PaymentSettings:
        settings = await self.payment_repo.get_by_id(settings_id)
        if not settings:
            raise ValidationError("Payment settings not found")

        old_values = {
            "telebirr_number": settings.telebirr_number,
            "account_holder_name": settings.account_holder_name,
            "deposit_instructions": settings.deposit_instructions,
            "min_deposit": str(settings.min_deposit),
            "max_deposit": str(settings.max_deposit),
            "is_deposit_enabled": settings.is_deposit_enabled,
            "auto_credit_enabled": settings.auto_credit_enabled,
            "maintenance_message": settings.maintenance_message,
            "is_active": settings.is_active,
        }

        for key, value in updates.items():
            if hasattr(settings, key):
                setattr(settings, key, value)

        await self.db.flush()
        await self.db.refresh(settings)

        new_values = {
            "telebirr_number": settings.telebirr_number,
            "account_holder_name": settings.account_holder_name,
            "deposit_instructions": settings.deposit_instructions,
            "min_deposit": str(settings.min_deposit),
            "max_deposit": str(settings.max_deposit),
            "is_deposit_enabled": settings.is_deposit_enabled,
            "auto_credit_enabled": settings.auto_credit_enabled,
            "maintenance_message": settings.maintenance_message,
            "is_active": settings.is_active,
        }

        await self.audit_service.log(
            actor_id=actor_id,
            action="payment_settings_updated",
            entity_type="payment_settings",
            entity_id=settings_id,
            old_value=old_values,
            new_value=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        await AdminChannel.broadcast(
            EventType.PAYMENT_SETTINGS_UPDATED,
            {
                "settings": {
                    "id": str(settings.id),
                    "telebirr_number": settings.telebirr_number,
                    "account_holder_name": settings.account_holder_name,
                    "deposit_instructions": settings.deposit_instructions,
                    "min_deposit": str(settings.min_deposit),
                    "max_deposit": str(settings.max_deposit),
                    "is_deposit_enabled": settings.is_deposit_enabled,
                    "auto_credit_enabled": settings.auto_credit_enabled,
                    "maintenance_message": settings.maintenance_message,
                    "is_active": settings.is_active,
                }
            },
        )

        return settings

    async def create_settings(self, initial_data: dict[str, Any]) -> PaymentSettings:
        settings = PaymentSettings(**initial_data)
        return await self.payment_repo.create(settings)

    async def get_or_create_default(self) -> PaymentSettings:
        settings = await self.payment_repo.get_active()
        if settings:
            return settings
        default_settings = PaymentSettings(
            telebirr_number="",
            account_holder_name="",
            deposit_instructions="Send money to the Telebirr number below and paste the SMS confirmation.",
            min_deposit=Decimal("10.00"),
            max_deposit=Decimal("10000.00"),
            is_deposit_enabled=True,
            auto_credit_enabled=False,
            maintenance_message=None,
            is_active=True,
        )
        return await self.payment_repo.create(default_settings)

    def validate_settings(self, data: dict[str, Any]) -> None:
        min_deposit = data.get("min_deposit")
        max_deposit = data.get("max_deposit")
        if min_deposit is not None and min_deposit <= 0:
            raise ValidationError("Minimum deposit must be positive")
        if max_deposit is not None and max_deposit <= 0:
            raise ValidationError("Maximum deposit must be positive")
        if min_deposit is not None and max_deposit is not None and max_deposit <= min_deposit:
            raise ValidationError("Maximum deposit must be greater than minimum deposit")

        telebirr_number = data.get("telebirr_number")
        if telebirr_number is not None and not telebirr_number.startswith("+251"):
            raise ValidationError("Telebirr number must start with +251")
