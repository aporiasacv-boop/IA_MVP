"""create performance_metrics table

Revision ID: 005_create_performance_metrics
Revises: 004_create_executive_summaries
Create Date: 2026-06-23 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005_create_performance_metrics"
down_revision: Union[str, None] = "004_create_executive_summaries"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "performance_metrics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("request_id", sa.String(length=36), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("handled_by", sa.String(length=50), nullable=False),
        sa.Column("operation_time_ms", sa.Float(), nullable=True),
        sa.Column("entity_time_ms", sa.Float(), nullable=True),
        sa.Column("intent_time_ms", sa.Float(), nullable=True),
        sa.Column("planner_time_ms", sa.Float(), nullable=True),
        sa.Column("executor_time_ms", sa.Float(), nullable=True),
        sa.Column("database_time_ms", sa.Float(), nullable=True),
        sa.Column("response_time_ms", sa.Float(), nullable=True),
        sa.Column("legacy_chat_time_ms", sa.Float(), nullable=True),
        sa.Column("ollama_time_ms", sa.Float(), nullable=True),
        sa.Column("total_time_ms", sa.Float(), nullable=False),
        sa.Column("query_type", sa.String(length=100), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("request_id"),
    )
    op.create_index(
        "ix_performance_metrics_created_at",
        "performance_metrics",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "ix_performance_metrics_handled_by",
        "performance_metrics",
        ["handled_by"],
        unique=False,
    )
    op.create_index(
        "ix_performance_metrics_question",
        "performance_metrics",
        ["question"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_performance_metrics_question", table_name="performance_metrics")
    op.drop_index("ix_performance_metrics_handled_by", table_name="performance_metrics")
    op.drop_index("ix_performance_metrics_created_at", table_name="performance_metrics")
    op.drop_table("performance_metrics")
