"""initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2024-07-14

"""
from typing import Any, Optional

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "001_initial_schema"
down_revision: Optional[str] = None
branch_labels: Optional[str] = None
depends_on: Optional[str] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("telegram_id", sa.Integer(), nullable=False, unique=True, index=True),
        sa.Column("username", sa.String(255), nullable=True),
        sa.Column("first_name", sa.String(255), nullable=True),
        sa.Column("last_name", sa.String(255), nullable=True),
        sa.Column("phone_number", sa.String(20), nullable=True),
        sa.Column("language", sa.String(10), server_default="am", nullable=False),
        sa.Column("status", sa.String(20), server_default="active", nullable=False),
        sa.Column("is_admin", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("last_seen", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "wallets",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), unique=True, nullable=False),
        sa.Column("balance", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("bonus_balance", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("jackpot_balance", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("total_deposited", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("total_withdrawn", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("total_won", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("total_spent", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "wallet_transactions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("wallet_id", UUID(as_uuid=True), sa.ForeignKey("wallets.id"), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), server_default="pending", nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("balance_before", sa.Numeric(18, 2), nullable=False),
        sa.Column("balance_after", sa.Numeric(18, 2), nullable=False),
        sa.Column("reference_id", sa.String(255), nullable=True, index=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("metadata", JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("approved_by", UUID(as_uuid=True), nullable=True),
    )

    op.create_table(
        "room_templates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("entry_fee", sa.Numeric(18, 2), nullable=False),
        sa.Column("max_cards_per_player", sa.Integer(), server_default="1", nullable=False),
        sa.Column("max_players", sa.Integer(), nullable=False),
        sa.Column("min_players", sa.Integer(), nullable=False),
        sa.Column("winning_pattern", sa.String(100), nullable=False),
        sa.Column("ball_calling_speed", sa.Integer(), server_default="3", nullable=False),
        sa.Column("house_percentage", sa.Numeric(5, 2), nullable=False),
        sa.Column("referral_percentage", sa.Numeric(5, 2), server_default="0", nullable=False),
        sa.Column("bonus_percentage", sa.Numeric(5, 2), server_default="0", nullable=False),
        sa.Column("jackpot_percentage", sa.Numeric(5, 2), server_default="0", nullable=False),
        sa.Column("visibility", sa.String(20), server_default="public", nullable=False),
        sa.Column("status", sa.String(20), server_default="draft", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
    )

    op.create_table(
        "rooms",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("template_id", UUID(as_uuid=True), sa.ForeignKey("room_templates.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("game_id", UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("status", sa.String(20), server_default="active", nullable=False),
        sa.Column("current_players", sa.Integer(), server_default="0", nullable=False),
        sa.Column("cards_sold", sa.Integer(), server_default="0", nullable=False),
        sa.Column("prize_pool", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "games",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("room_id", UUID(as_uuid=True), sa.ForeignKey("rooms.id"), nullable=False, index=True),
        sa.Column("status", sa.String(20), server_default="waiting", nullable=False, index=True),
        sa.Column("seed", sa.String(255), nullable=True),
        sa.Column("seed_hash", sa.String(255), nullable=True, index=True),
        sa.Column("called_numbers", JSONB(), server_default="[]", nullable=False),
        sa.Column("current_number", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("winner_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("winning_pattern", sa.String(100), nullable=True),
        sa.Column("prize_amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "cards",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("room_id", UUID(as_uuid=True), sa.ForeignKey("rooms.id"), nullable=False, index=True),
        sa.Column("numbers", JSONB(), nullable=False),
        sa.Column("pattern_index", sa.Integer(), nullable=False),
        sa.Column("is_sold", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "purchased_cards",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("game_id", UUID(as_uuid=True), sa.ForeignKey("games.id"), nullable=False, index=True),
        sa.Column("card_id", UUID(as_uuid=True), sa.ForeignKey("cards.id"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("marks", JSONB(), server_default="[]", nullable=True),
        sa.Column("is_winner", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("purchased_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "called_numbers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("game_id", UUID(as_uuid=True), sa.ForeignKey("games.id"), nullable=False, index=True),
        sa.Column("number", sa.Integer(), nullable=False, index=True),
        sa.Column("called_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "winning_claims",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("game_id", UUID(as_uuid=True), sa.ForeignKey("games.id"), nullable=False, index=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("card_id", UUID(as_uuid=True), sa.ForeignKey("cards.id"), nullable=False),
        sa.Column("pattern", sa.String(100), nullable=False),
        sa.Column("is_verified", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("claimed_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "prize_payouts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("game_id", UUID(as_uuid=True), sa.ForeignKey("games.id"), nullable=False, index=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("transaction_id", UUID(as_uuid=True), sa.ForeignKey("wallet_transactions.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "deposits",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("status", sa.String(50), server_default="pending", nullable=False),
        sa.Column("transaction_id", UUID(as_uuid=True), sa.ForeignKey("wallet_transactions.id"), nullable=True),
        sa.Column("proof_url", sa.String(500), nullable=True),
        sa.Column("reviewed_by", UUID(as_uuid=True), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "withdrawals",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("phone_number", sa.String(20), nullable=False),
        sa.Column("status", sa.String(50), server_default="pending", nullable=False),
        sa.Column("transaction_id", UUID(as_uuid=True), sa.ForeignKey("wallet_transactions.id"), nullable=True),
        sa.Column("reviewed_by", UUID(as_uuid=True), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "announcements",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("priority", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("published_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("is_read", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("data", JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "achievements",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("threshold", sa.Integer(), nullable=False),
        sa.Column("reward_amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("icon", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "achievement_progress",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("achievement_id", UUID(as_uuid=True), sa.ForeignKey("achievements.id"), nullable=False, index=True),
        sa.Column("current_value", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_completed", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "referral_accounts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("referrer_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("referred_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("reward_percentage", sa.Numeric(5, 2), nullable=False),
        sa.Column("total_earned", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "referral_rewards",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("referral_id", UUID(as_uuid=True), sa.ForeignKey("referral_accounts.id"), nullable=False, index=True),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("transaction_id", UUID(as_uuid=True), sa.ForeignKey("wallet_transactions.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "daily_rewards",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("day", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("claimed_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "player_statistics",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), unique=True, nullable=False),
        sa.Column("games_played", sa.Integer(), server_default="0", nullable=False),
        sa.Column("games_won", sa.Integer(), server_default="0", nullable=False),
        sa.Column("win_rate", sa.Numeric(5, 2), server_default="0", nullable=False),
        sa.Column("current_streak", sa.Integer(), server_default="0", nullable=False),
        sa.Column("best_streak", sa.Integer(), server_default="0", nullable=False),
        sa.Column("cards_purchased", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_deposited", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("total_withdrawn", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("total_won", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("referral_earnings", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "leaderboards",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("period", sa.String(50), nullable=False, index=True),
        sa.Column("score", sa.Numeric(18, 2), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "admin_actions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("admin_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("action", sa.String(255), nullable=False),
        sa.Column("target_type", sa.String(100), nullable=True),
        sa.Column("target_id", UUID(as_uuid=True), nullable=True),
        sa.Column("details", JSONB(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("actor_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True, index=True),
        sa.Column("action", sa.String(255), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=True),
        sa.Column("entity_id", UUID(as_uuid=True), nullable=True),
        sa.Column("old_value", JSONB(), nullable=True),
        sa.Column("new_value", JSONB(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False, index=True),
    )

    op.create_table(
        "localizations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("language_code", sa.String(10), nullable=False, index=True),
        sa.Column("key", sa.String(255), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "settings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("key", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_public", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "feature_flags",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("key", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("is_enabled", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "maintenance_mode",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "system_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("level", sa.String(20), nullable=False, index=True),
        sa.Column("source", sa.String(255), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("data", JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False, index=True),
    )


def downgrade() -> None:
    op.drop_table("system_logs")
    op.drop_table("maintenance_mode")
    op.drop_table("feature_flags")
    op.drop_table("settings")
    op.drop_table("localizations")
    op.drop_table("audit_logs")
    op.drop_table("admin_actions")
    op.drop_table("leaderboards")
    op.drop_table("player_statistics")
    op.drop_table("daily_rewards")
    op.drop_table("referral_rewards")
    op.drop_table("referral_accounts")
    op.drop_table("achievement_progress")
    op.drop_table("achievements")
    op.drop_table("notifications")
    op.drop_table("announcements")
    op.drop_table("withdrawals")
    op.drop_table("deposits")
    op.drop_table("prize_payouts")
    op.drop_table("winning_claims")
    op.drop_table("called_numbers")
    op.drop_table("purchased_cards")
    op.drop_table("cards")
    op.drop_table("games")
    op.drop_table("rooms")
    op.drop_table("room_templates")
    op.drop_table("wallet_transactions")
    op.drop_table("wallets")
    op.drop_table("users")
