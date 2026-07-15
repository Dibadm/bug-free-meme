from __future__ import annotations

from typing import Any


class HabeshaBetError(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(message)


class NotFoundError(HabeshaBetError):
    """Resource not found."""

    status_code = 404


class ConflictError(HabeshaBetError):
    """Resource conflict."""

    status_code = 409


class ValidationError(HabeshaBetError):
    """Input validation failed."""

    status_code = 422


class InsufficientFundsError(HabeshaBetError):
    """Insufficient wallet balance."""

    status_code = 400


class InsufficientBalanceError(HabeshaBetError):
    """Insufficient wallet balance."""

    status_code = 400


class RoomClosedError(HabeshaBetError):
    """Room is not accepting joins."""

    status_code = 400


class DuplicateCardError(HabeshaBetError):
    """Card already purchased."""

    status_code = 409


class InvalidWithdrawalError(HabeshaBetError):
    """Withdrawal request is invalid."""

    status_code = 400


class InvalidDepositError(HabeshaBetError):
    """Deposit request is invalid."""

    status_code = 400


class InvalidGameStateError(HabeshaBetError):
    """Game is in invalid state for requested action."""

    status_code = 400


class AuthenticationError(HabeshaBetError):
    """Authentication failed."""

    status_code = 401


class AuthorizationError(HabeshaBetError):
    """Authorization failed."""

    status_code = 403


class RateLimitError(HabeshaBetError):
    """Rate limit exceeded."""

    status_code = 429


class GameError(HabeshaBetError):
    """Game logic error."""

    status_code = 400


class DatabaseError(HabeshaBetError):
    """Database operation failed."""

    status_code = 500
