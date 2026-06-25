"""add suggested_questions_count to performance_metrics

Revision ID: 006_add_suggested_questions_metrics
Revises: 005_create_performance_metrics
Create Date: 2026-06-23 18:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "006_add_suggested_questions_metrics"
down_revision: Union[str, None] = "005_create_performance_metrics"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "performance_metrics",
        sa.Column("suggested_questions_count", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("performance_metrics", "suggested_questions_count")
