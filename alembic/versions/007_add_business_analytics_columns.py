"""add business analytics columns to performance_metrics

Revision ID: 007_add_business_analytics_columns
Revises: 006_add_suggested_questions_metrics
Create Date: 2026-06-24 20:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "007_add_business_analytics_columns"
down_revision: Union[str, None] = "006_add_suggested_questions_metrics"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "performance_metrics",
        sa.Column("route_type", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "performance_metrics",
        sa.Column("response_success", sa.Boolean(), nullable=True),
    )
    op.add_column(
        "performance_metrics",
        sa.Column("deterministic_resolution", sa.Boolean(), nullable=True),
    )
    op.add_column(
        "performance_metrics",
        sa.Column("used_ai", sa.Boolean(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("performance_metrics", "used_ai")
    op.drop_column("performance_metrics", "deterministic_resolution")
    op.drop_column("performance_metrics", "response_success")
    op.drop_column("performance_metrics", "route_type")
