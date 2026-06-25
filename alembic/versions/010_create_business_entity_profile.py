"""create business entity profile table

Revision ID: 010_create_business_entity_profile
Revises: 009_create_canonical_business_entity
Create Date: 2026-06-24 14:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "010_create_business_entity_profile"
down_revision: Union[str, None] = "009_create_canonical_business_entity"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "business_entity_profile",
        sa.Column("profile_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("canonical_id", sa.BigInteger(), nullable=False),
        sa.Column("total_movements", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("total_amount", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0"),
        sa.Column("average_amount", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0"),
        sa.Column("first_seen", sa.Date(), nullable=True),
        sa.Column("last_seen", sa.Date(), nullable=True),
        sa.Column("active_months", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("active_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("debit_amount", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0"),
        sa.Column("credit_amount", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0"),
        sa.Column("debit_credit_ratio", sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column("related_accounts_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("related_counterparties_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("monthly_distribution", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("currencies", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("journals", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("dimensions_used", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("top_accounts", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("top_counterparties", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("profile_completeness", sa.Numeric(precision=5, scale=4), nullable=False, server_default="0"),
        sa.Column("generated_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["canonical_id"], ["canonical_business_entity.canonical_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("profile_id"),
        sa.UniqueConstraint("canonical_id", name="uq_bep_canonical_id"),
    )
    op.create_index("ix_bep_total_movements", "business_entity_profile", ["total_movements"])
    op.create_index("ix_bep_last_seen", "business_entity_profile", ["last_seen"])
    op.create_index("ix_bep_profile_completeness", "business_entity_profile", ["profile_completeness"])


def downgrade() -> None:
    op.drop_index("ix_bep_profile_completeness", table_name="business_entity_profile")
    op.drop_index("ix_bep_last_seen", table_name="business_entity_profile")
    op.drop_index("ix_bep_total_movements", table_name="business_entity_profile")
    op.drop_table("business_entity_profile")
