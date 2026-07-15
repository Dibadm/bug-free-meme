from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.models.models import (
    DailyReward,
    NotificationPreference,
    PlayerStatistics,
    Session,
    User,
    UserProfile,
    UserRole,
    UserStatus,
    Wallet,
)
from app.repositories import NotificationPreferenceRepository, SessionRepository, UserProfileRepository, UserRepository
from app.services.audit_service import AuditService
from app.services.base import BaseService
from app.services.leaderboard_service import LeaderboardService
from app.services.wallet_service import WalletService


class AuthService(BaseService):
    def __init__(self, db: Any) -> None:
        super().__init__(db)
        self.user_repo = UserRepository(db)
        self.session_repo = SessionRepository(db)
        self.profile_repo = UserProfileRepository(db)
        self.notification_pref_repo = NotificationPreferenceRepository(db)
        self.wallet_service = WalletService(db)
        self.audit_service = AuditService(db)
        self.leaderboard_service = LeaderboardService(db)

    @staticmethod
    def validate_telegram_init_data(init_data: str, secret_token: str) -> dict[str, Any]:
        if not init_data:
            raise ValidationError("Missing init_data")

        pairs = dict(pair.split("=", 1) for pair in init_data.split("&") if "=" in pair)

        received_hash = pairs.pop("hash", None)
        if not received_hash:
            raise ValidationError("Missing hash in init_data")

        auth_date = int(pairs.get("auth_date", 0))
        if auth_date and (datetime.now(timezone.utc).timestamp() - auth_date) > 86400:
            raise ValidationError("init_data expired")

        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))
        secret_key = hmac.new(secret_token.encode(), b"WebAppData", hashlib.sha256).digest()
        expected_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(expected_hash, received_hash):
            raise ValidationError("Invalid init_data signature")

        return pairs

    def generate_referral_code(self) -> str:
        return secrets.token_hex(4).upper()

    async def authenticate(self, init_data: str, ip_address: str | None = None, user_agent: str | None = None) -> tuple[User, bool]:
        validated_data = self.validate_telegram_init_data(init_data, settings.TELEGRAM_SECRET_TOKEN)

        telegram_id = int(validated_data.get("id", 0))
        if not telegram_id:
            raise ValidationError("Invalid telegram_id in init_data")

        user = await self.user_repo.get_by_telegram_id(telegram_id)
        is_new_user = False

        if not user:
            is_new_user = True
            referral_code = validated_data.get("referral_code")
            referrer = None
            if referral_code:
                referrer = await self.user_repo.find_one(referral_code=referral_code, deleted_at=None)

            user = User(
                telegram_id=telegram_id,
                username=validated_data.get("username"),
                first_name=validated_data.get("first_name"),
                last_name=validated_data.get("last_name"),
                language=validated_data.get("language", "am"),
                status=UserStatus.REGISTERED,
                role=UserRole.PLAYER,
                is_verified=False,
                last_seen=datetime.now(timezone.utc),
                last_login=datetime.now(timezone.utc),
                referral_code=self.generate_referral_code(),
            )
            await self.user_repo.create(user)

            wallet = Wallet(user_id=user.id)
            self.db.add(wallet)

            stats = PlayerStatistics(user_id=user.id)
            self.db.add(stats)

            profile = UserProfile(user_id=user.id)
            self.db.add(profile)

            default_prefs = [
                NotificationPreference(user_id=user.id, notification_type="game", enabled=True),
                NotificationPreference(user_id=user.id, notification_type="wallet", enabled=True),
                NotificationPreference(user_id=user.id, notification_type="announcement", enabled=True),
                NotificationPreference(user_id=user.id, notification_type="admin", enabled=True),
            ]
            self.db.add_all(default_prefs)

            await self.db.flush()

            leaderboard_service = LeaderboardService(self.db)
            await leaderboard_service.update_score(user.id, "global", 0)

            await self.audit_service.log(
                actor_id=user.id,
                action="user_registered",
                entity_type="user",
                entity_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
            )
        else:
            user.username = validated_data.get("username", user.username)
            user.first_name = validated_data.get("first_name", user.first_name)
            user.last_name = validated_data.get("last_name", user.last_name)
            user.language = validated_data.get("language", user.language)
            user.last_seen = datetime.now(timezone.utc)
            user.last_login = datetime.now(timezone.utc)

            if user.status == UserStatus.DELETED:
                raise ValidationError("User account is deleted")

            await self.db.flush()
            await self.db.refresh(user)

            await self.audit_service.log(
                actor_id=user.id,
                action="user_login",
                entity_type="user",
                entity_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
            )

        return user, is_new_user

    async def create_session(self, user: User, token_hash: str, device_info: str | None = None, ip_address: str | None = None, user_agent: str | None = None, expires_delta: timedelta | None = None) -> Session:
        expires_at = datetime.now(timezone.utc) + (expires_delta or timedelta(days=30))
        session = Session(
            user_id=user.id,
            token_hash=token_hash,
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
        )
        return await self.session_repo.create(session)

    async def get_session_by_token(self, token_hash: str) -> Session | None:
        return await self.session_repo.get_by_token_hash(token_hash)

    async def logout(self, session_id: UUID) -> None:
        await self.session_repo.revoke_session(session_id)

    async def logout_all(self, user_id: UUID) -> None:
        await self.session_repo.revoke_all_user_sessions(user_id)

    async def get_user_sessions(self, user_id: UUID) -> list[Session]:
        return await self.session_repo.get_active_sessions_by_user(user_id)
