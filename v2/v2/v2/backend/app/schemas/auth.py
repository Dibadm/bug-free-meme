from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas import BaseSchema


class TelegramAuthData(BaseSchema):
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    language: str = "am"
    auth_date: int | None = None
    hash: str | None = None
    photo_url: str | None = None
    referral_code: str | None = None


class LoginRequest(BaseSchema):
    init_data: str


class LoginResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: UUID
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    role: str
    is_new_user: bool


class RefreshRequest(BaseSchema):
    refresh_token: str


class RefreshResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class SessionRead(BaseSchema):
    id: UUID
    device_info: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    expires_at: datetime
    last_used_at: datetime
    created_at: datetime
    is_revoked: bool = False

    model_config = ConfigDict(from_attributes=True)


class ProfileUpdate(BaseSchema):
    language: str | None = None
    phone_number: str | None = None
    avatar_url: str | None = None
    display_name: str | None = None
    notification_preferences: dict | None = None


class ProfileRead(BaseSchema):
    id: UUID
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    language: str
    role: str
    avatar_url: str | None = None
    display_name: str | None = None
    privacy_settings: dict | None = None
    last_login: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReferralApply(BaseSchema):
    referral_code: str


class ReferralRead(BaseSchema):
    id: UUID
    referrer_id: UUID
    referred_id: UUID
    reward_percentage: float
    total_earned: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
