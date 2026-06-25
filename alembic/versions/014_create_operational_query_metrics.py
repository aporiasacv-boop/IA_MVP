"""create operational_query_metrics table

Revision ID: 014_create_operational_query_metrics
Revises: 013_create_enterprise_reasoning_object
Create Date: 2026-06-24 22:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "014_create_operational_query_metrics"
down_revision: Union[str, None] = "013_create_enterprise_reasoning_object"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "operational_query_metrics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("request_id", sa.String(length=64), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("session_id", sa.String(length=64), nullable=True),
        sa.Column("handled_by", sa.String(length=50), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("user_id", sa.String(length=100), nullable=True),
        sa.Column("channel", sa.String(length=50), nullable=False),
        sa.Column("query_type", sa.String(length=100), nullable=True),
        sa.Column("verb", sa.String(length=50), nullable=True),
        sa.Column("intent", sa.String(length=100), nullable=True),
        sa.Column("response_time_ms", sa.Float(), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=False),
        sa.Column("output_tokens", sa.Integer(), nullable=False),
        sa.Column("total_tokens", sa.Integer(), nullable=False),
        sa.Column("estimated_tokens", sa.Integer(), nullable=False),
        sa.Column("token_source", sa.String(length=20), nullable=False),
        sa.Column("cache_hit", sa.Boolean(), nullable=False),
        sa.Column("knowledge_hit", sa.Boolean(), nullable=False),
        sa.Column("pipeline_hit", sa.Boolean(), nullable=False),
        sa.Column("executive_reasoning", sa.Boolean(), nullable=False),
        sa.Column("llm_used", sa.Boolean(), nullable=False),
        sa.Column("llm_provider", sa.String(length=50), nullable=True),
        sa.Column("llm_model", sa.String(length=100), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("cost_usd", sa.Float(), nullable=False),
        sa.Column("cost_mxn", sa.Float(), nullable=False),
        sa.Column("avoided_cost_usd", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("request_id"),
    )
    op.create_index("ix_operational_query_metrics_timestamp", "operational_query_metrics", ["timestamp"])
    op.create_index("ix_operational_query_metrics_handled_by", "operational_query_metrics", ["handled_by"])


def downgrade() -> None:
    op.drop_index("ix_operational_query_metrics_handled_by", table_name="operational_query_metrics")
    op.drop_index("ix_operational_query_metrics_timestamp", table_name="operational_query_metrics")
    op.drop_table("operational_query_metrics")
