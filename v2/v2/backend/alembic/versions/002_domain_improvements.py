"""Domain improvements - constraints, indexes, soft deletes

Revision ID: 002_domain_improvements
Revises: 001_initial_schema
Create Date: 2024-07-14 01:00:00.000000
"""
from typing import Any

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID


revision: str = "002_domain_improvements"
down_revision: str = "001_initial_schema"
branch_labels: Any = None
depends_on: Any = None


def upgrade() -> None:
    op.create_unique_constraint("uq_leaderboards_user_period", "leaderboards", ["user_id", "period"])
    op.create_unique_constraint("uq_achievement_progress_user_achievement", "achievement_progress", ["user_id", "achievement_id"])
    op.create_unique_constraint("uq_referral_accounts_referrer_referred", "referral_accounts", ["referrer_id", "referred_id"])
    op.create_unique_constraint("uq_daily_rewards_user_day", "daily_rewards", ["user_id", "day"])
    op.create_unique_constraint("uq_called_numbers_game_number", "called_numbers", ["game_id", "number"])
    op.create_unique_constraint("uq_purchased_cards_game_card_user", "purchased_cards", ["game_id", "card_id", "user_id"])
    op.create_unique_constraint("uq_winning_claims_game_user_card", "winning_claims", ["game_id", "user_id", "card_id"])
    op.create_unique_constraint("uq_localizations_lang_key", "localizations", ["language_code", "key"])

    op.create_index("ix_games_room_id_status", "games", ["room_id", "status"])
    op.create_index("ix_wallet_transactions_wallet_type_status", "wallet_transactions", ["wallet_id", "type", "status"])
    op.create_index("ix_notifications_user_read", "notifications", ["user_id", "is_read"])

    op.add_column("users", sa.Column("deleted_at", sa.DateTime(), nullable=True))
    op.add_column("room_templates", sa.Column("deleted_at", sa.DateTime(), nullable=True))
    op.add_column("rooms", sa.Column("deleted_at", sa.DateTime(), nullable=True))
    op.add_column("games", sa.Column("deleted_at", sa.DateTime(), nullable=True))
    op.add_column("announcements", sa.Column("deleted_at", sa.DateTime(), nullable=True))

    op.alter_column("users", "created_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("users", "updated_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("wallets", "created_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("wallets", "updated_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("wallet_transactions", "created_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("wallet_transactions", "updated_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("room_templates", "created_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("room_templates", "updated_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("rooms", "created_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("rooms", "updated_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("games", "created_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("games", "updated_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("cards", "created_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("purchased_cards", "purchased_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("called_numbers", "called_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("winning_claims", "claimed_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("prize_payouts", "created_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("deposits", "created_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("deposits", "updated_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("withdrawals", "created_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("withdrawals", "updated_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("announcements", "created_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("notifications", "created_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("achievements", "created_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("achievement_progress", "created_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("achievement_progress", "updated_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("referral_accounts", "created_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("referral_rewards", "created_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("daily_rewards", "claimed_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("player_statistics", "created_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("player_statistics", "updated_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("leaderboards", "created_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("leaderboards", "updated_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("admin_actions", "created_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("audit_logs", "created_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("localizations", "created_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("localizations", "updated_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("settings", "created_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("settings", "updated_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("feature_flags", "created_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("feature_flags", "updated_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("maintenance_mode", "created_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("system_logs", "created_at", existing_type=sa.DateTime(), nullable=False)


def downgrade() -> None:
    op.alter_column("system_logs", "created_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("maintenance_mode", "created_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("feature_flags", "updated_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("feature_flags", "created_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("settings", "updated_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("settings", "created_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("localizations", "updated_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("localizations", "created_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("audit_logs", "created_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("admin_actions", "created_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("leaderboards", "updated_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("leaderboards", "created_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("player_statistics", "updated_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("player_statistics", "created_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("daily_rewards", "claimed_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("referral_rewards", "created_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("referral_accounts", "created_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("achievement_progress", "updated_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("achievement_progress", "created_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("achievements", "created_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("notifications", "created_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("announcements", "created_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("withdrawals", "updated_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("withdrawals", "created_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("deposits", "updated_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("deposits", "created_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("prize_payouts", "created_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("winning_claims", "claimed_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("called_numbers", "called_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("purchased_cards", "purchased_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("cards", "created_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("games", "updated_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("games", "created_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("rooms", "updated_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("rooms", "created_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("room_templates", "updated_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("room_templates", "created_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("wallet_transactions", "updated_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("wallet_transactions", "created_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("wallets", "updated_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("wallets", "created_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("users", "updated_at", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("users", "created_at", existing_type=sa.DateTime(), nullable=True)

    op.drop_column("announcements", "deleted_at")
    op.drop_column("games", "deleted_at")
    op.drop_column("rooms", "deleted_at")
    op.drop_column("room_templates", "deleted_at")
    op.drop_column("users", "deleted_at")

    op.drop_index("ix_notifications_user_read", table_name="notifications")
    op.drop_index("ix_wallet_transactions_wallet_type_status", table_name="wallet_transactions")
    op.drop_index("ix_games_room_id_status", table_name="games")

    op.drop_constraint("uq_localizations_lang_key", "localizations", type_="unique")
    op.drop_constraint("uq_winning_claims_game_user_card", "winning_claims", type_="unique")
    op.drop_constraint("uq_purchased_cards_game_card_user", "purchased_cards", type_="unique")
    op.drop_constraint("uq_called_numbers_game_number", "called_numbers", type_="unique")
    op.drop_constraint("uq_daily_rewards_user_day", "daily_rewards", type_="unique")
    op.drop_constraint("uq_referral_accounts_referrer_referred", "referral_accounts", type_="unique")
    op.drop_constraint("uq_achievement_progress_user_achievement", "achievement_progress", type_="unique")
    op.drop_constraint("uq_leaderboards_user_period", "leaderboards", type_="unique")
