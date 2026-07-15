"""Payment settings and SMS verification

Revision ID: 004_payment_settings
Revises: 003_auth_lifecycle
Create Date: 2024-07-15 00:00:00.000000
"""
from typing import Any

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID


revision: str = "004_payment_settings"
down_revision: str = "003_auth_lifecycle"
branch_labels: Any = None
depends_on: Any = None


def upgrade() -> None:
    op.create_table(
        "payment_settings",
        sa.Column("id", PG_UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("telebirr_number", sa.String(length=20), nullable=False),
        sa.Column("account_holder_name", sa.String(length=255), nullable=False),
        sa.Column("deposit_instructions", sa.Text(), nullable=False),
        sa.Column("min_deposit", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("max_deposit", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("is_deposit_enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("auto_credit_enabled", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("maintenance_message", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.add_column("deposits", sa.Column("sms_code", sa.String(length=10), nullable=True))
    op.add_column("deposits", sa.Column("sms_sent_to", sa.String(length=20), nullable=True))
    op.add_column("deposits", sa.Column("sms_verified_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("deposits", "sms_verified_at")
    op.drop_column("deposits", "sms_sent_to")
    op.drop_column("deposits", "sms_code")
    op.drop_table("payment_settings")
