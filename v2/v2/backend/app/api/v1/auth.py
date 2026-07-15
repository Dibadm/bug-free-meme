from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    ProfileRead,
    ProfileUpdate,
    ReferralApply,
    ReferralRead,
    SessionRead,
    TelegramAuthData,
)
from app.services import AuthService, ProfileService, ReferralService
from app.services.auth_service import AuthService as _AuthService

router = APIRouter()


def _hash_token(token: str) -> str:
    from hashlib import sha256
    return sha256(token.encode()).hexdigest()


@router.post("/auth/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    auth_service = AuthService(db)
    user, is_new_user = await auth_service.authenticate(
        init_data=request.init_data,
        ip_address=None,
        user_agent=None,
    )

    access_token = _AuthService.create_access_token(
        subject=user.id,
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        extra_claims={"telegram_id": user.telegram_id, "role": user.role.value},
    )

    token_hash = _hash_token(access_token)
    await auth_service.create_session(user, token_hash)

    return LoginResponse(
        access_token=access_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.value,
        is_new_user=is_new_user,
    )


@router.post("/auth/logout")
async def logout(
    token: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    auth_service = AuthService(db)
    token_hash = _hash_token(token)
    session = await auth_service.get_session_by_token(token_hash)
    if session:
        await auth_service.logout(session.id)
    return {"status": "logged_out"}


@router.post("/auth/refresh", response_model=LoginResponse)
async def refresh(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    auth_service = AuthService(db)
    user, is_new_user = await auth_service.authenticate(
        init_data=request.init_data,
        ip_address=None,
        user_agent=None,
    )

    access_token = _AuthService.create_access_token(
        subject=user.id,
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        extra_claims={"telegram_id": user.telegram_id, "role": user.role.value},
    )

    token_hash = _hash_token(access_token)
    await auth_service.create_session(user, token_hash)

    return LoginResponse(
        access_token=access_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.value,
        is_new_user=is_new_user,
    )


@router.get("/auth/me", response_model=ProfileRead)
async def get_me(
    token: str,
    db: AsyncSession = Depends(get_db),
) -> ProfileRead:
    auth_service = AuthService(db)
    token_hash = _hash_token(token)
    session = await auth_service.get_session_by_token(token_hash)
    if not session or session.revoked_at or session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")

    user = await auth_service.user_repo.get_by_id(session.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    profile = await auth_service.profile_repo.get_by_user_id(user.id)
    return ProfileRead(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        language=user.language,
        role=user.role.value,
        avatar_url=profile.avatar_url if profile else None,
        display_name=profile.display_name if profile else None,
        privacy_settings=profile.privacy_settings if profile else None,
        last_login=user.last_login,
        created_at=user.created_at,
    )


@router.patch("/profile", response_model=ProfileRead)
async def update_profile(
    profile_data: ProfileUpdate,
    token: str,
    db: AsyncSession = Depends(get_db),
) -> ProfileRead:
    auth_service = AuthService(db)
    token_hash = _hash_token(token)
    session = await auth_service.get_session_by_token(token_hash)
    if not session or session.revoked_at or session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")

    user = await auth_service.user_repo.get_by_id(session.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    profile_service = ProfileService(db)

    if profile_data.language is not None:
        user.language = profile_data.language
    if profile_data.phone_number is not None:
        user.phone_number = profile_data.phone_number

    profile_update_data = profile_data.model_dump(exclude_unset=True)
    profile = await profile_service.update_profile(user.id, **profile_update_data)

    await db.flush()
    await db.refresh(user)

    return ProfileRead(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        language=user.language,
        role=user.role.value,
        avatar_url=profile.avatar_url if profile else None,
        display_name=profile.display_name if profile else None,
        privacy_settings=profile.privacy_settings if profile else None,
        last_login=user.last_login,
        created_at=user.created_at,
    )


@router.get("/sessions", response_model=list[SessionRead])
async def get_sessions(
    token: str,
    db: AsyncSession = Depends(get_db),
) -> list[SessionRead]:
    auth_service = AuthService(db)
    token_hash = _hash_token(token)
    session = await auth_service.get_session_by_token(token_hash)
    if not session or session.revoked_at or session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")

    sessions = await auth_service.get_user_sessions(session.user_id)
    return [
        SessionRead(
            id=s.id,
            device_info=s.device_info,
            ip_address=s.ip_address,
            user_agent=s.user_agent,
            expires_at=s.expires_at,
            last_used_at=s.last_used_at,
            created_at=s.created_at,
            is_revoked=s.revoked_at is not None,
        )
        for s in sessions
    ]


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: UUID,
    token: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    auth_service = AuthService(db)
    token_hash = _hash_token(token)
    current_session = await auth_service.get_session_by_token(token_hash)
    if not current_session or current_session.revoked_at or current_session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")

    if current_session.id == session_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot revoke current session")

    await auth_service.logout(session_id)
    return {"status": "revoked"}


@router.post("/referrals/apply", response_model=ReferralRead)
async def apply_referral(
    referral_data: ReferralApply,
    token: str,
    db: AsyncSession = Depends(get_db),
) -> ReferralRead:
    auth_service = AuthService(db)
    token_hash = _hash_token(token)
    session = await auth_service.get_session_by_token(token_hash)
    if not session or session.revoked_at or session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")

    referral_service = ReferralService(db)
    referral = await referral_service.apply_referral(session.user_id, referral_data.referral_code)
    return ReferralRead(
        id=referral.id,
        referrer_id=referral.referrer_id,
        referred_id=referral.referred_id,
        reward_percentage=float(referral.reward_percentage),
        total_earned=float(referral.total_earned),
        created_at=referral.created_at,
    )
