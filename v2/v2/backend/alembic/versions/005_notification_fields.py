"""Add missing notification columns

Revision ID: 005_notification_fields
Revises: 004_payment_settings
Create Date: 2026-07-15
"""
from typing import Any

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


revision: str = "005_notification_fields"
down_revision: str = "004_payment_settings"
branch_labels: Any = None
depends_on: Any = None


def upgrade() -> None:
    op.execute("CREATE TYPE notificationstatus AS ENUM ('PENDING', 'SCHEDULED', 'SENT', 'FAILED', 'READ')")
    op.add_column("notifications", sa.Column("read_at", sa.DateTime(), nullable=True))
    op.add_column("notifications", sa.Column("status", sa.Enum(name="notificationstatus"), server_default="PENDING", nullable=False))
    op.add_column("notifications", sa.Column("priority", sa.String(length=20), server_default="normal", nullable=False))
    op.add_column("notifications", sa.Column("scheduled_at", sa.DateTime(), nullable=True))
    op.add_column("notifications", sa.Column("sent_at", sa.DateTime(), nullable=True))
    op.add_column("notifications", sa.Column("retry_count", sa.Integer(), server_default="0", nullable=False))


def downgrade() -> None:
    op.drop_column("notifications", "retry_count")
    op.drop_column("notifications", "sent_at")
    op.drop_column("notifications", "scheduled_at")
    op.drop_column("notifications", "priority")
    op.drop_column("notifications", "status")
    op.drop_column("notifications", "read_at")
    op.execute("DROP TYPE notificationstatus")
