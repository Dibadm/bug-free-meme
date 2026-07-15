from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.permissions import PermissionMiddleware
from app.models.models import User, PaymentSettings
from app.schemas.admin import PaymentSettingsRead, PaymentSettingsUpdate
from app.schemas.wallet import PublicPaymentSettings
from app.services import AuditService, PaymentSettingsService

router = APIRouter()


@router.get("/payment-settings", response_model=PublicPaymentSettings)
async def get_public_payment_settings(db: AsyncSession = Depends(get_db)) -> PublicPaymentSettings:
    service = PaymentSettingsService(db)
    settings = await service.get_or_create_default()
    if not settings.is_deposit_enabled:
        return PublicPaymentSettings(
            telebirr_number="",
            account_holder_name="",
            deposit_instructions="Deposits are currently disabled.",
            min_deposit=0,
            max_deposit=0,
            is_deposit_enabled=False,
            maintenance_message=settings.maintenance_message or "Deposits are temporarily unavailable.",
        )
    return PublicPaymentSettings(
        telebirr_number=settings.telebirr_number,
        account_holder_name=settings.account_holder_name,
        deposit_instructions=settings.deposit_instructions,
        min_deposit=settings.min_deposit,
        max_deposit=settings.max_deposit,
        is_deposit_enabled=settings.is_deposit_enabled,
        maintenance_message=settings.maintenance_message,
    )


@router.get("/admin/payment-settings", response_model=PaymentSettingsRead)
async def get_admin_payment_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionMiddleware.require_role(UserRole.ADMIN)),
) -> PaymentSettingsRead:
    service = PaymentSettingsService(db)
    settings = await service.get_or_create_default()
    return PaymentSettingsRead.model_validate(settings)


@router.patch("/admin/payment-settings", response_model=PaymentSettingsRead)
async def update_admin_payment_settings(
    updates: PaymentSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionMiddleware.require_role(UserRole.ADMIN)),
    request: Request = None,
) -> PaymentSettingsRead:
    service = PaymentSettingsService(db)
    settings = await service.get_or_create_default()
    update_data = updates.model_dump(exclude_unset=True)
    service.validate_settings(update_data)
    updated = await service.update_settings(
        settings_id=settings.id,
        updates=update_data,
        actor_id=current_user.id,
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None,
    )
    return PaymentSettingsRead.model_validate(updated)
