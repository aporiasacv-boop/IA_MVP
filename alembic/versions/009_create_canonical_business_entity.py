"""create canonical business entity tables

Revision ID: 009_create_canonical_business_entity
Revises: 008_create_business_entity_master
Create Date: 2026-06-24 10:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "009_create_canonical_business_entity"
down_revision: Union[str, None] = "008_create_business_entity_master"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "canonical_business_entity",
        sa.Column("canonical_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("canonical_name", sa.String(length=255), nullable=False),
        sa.Column("normalized_name", sa.String(length=255), nullable=False),
        sa.Column("primary_rfc", sa.String(length=20), nullable=True),
        sa.Column("alias_count", sa.BigInteger(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("canonical_id"),
    )
    op.create_index("ix_cbe_normalized_name", "canonical_business_entity", ["normalized_name"])
    op.create_index("ix_cbe_primary_rfc", "canonical_business_entity", ["primary_rfc"])

    op.create_table(
        "business_entity_resolution",
        sa.Column("resolution_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("entity_id", sa.BigInteger(), nullable=False),
        sa.Column("canonical_id", sa.BigInteger(), nullable=False),
        sa.Column("resolution_rule", sa.String(length=80), nullable=False),
        sa.Column("resolution_score", sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["business_entity_master.entity_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["canonical_id"], ["canonical_business_entity.canonical_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("resolution_id"),
        sa.UniqueConstraint("entity_id", name="uq_ber_entity_id"),
    )
    op.create_index("ix_ber_canonical_id", "business_entity_resolution", ["canonical_id"])

    op.create_table(
        "canonical_entity_suggestion",
        sa.Column("suggestion_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("source_entity_id", sa.BigInteger(), nullable=False),
        sa.Column("candidate_entity_id", sa.BigInteger(), nullable=False),
        sa.Column("rule_used", sa.String(length=80), nullable=False),
        sa.Column("score", sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["source_entity_id"], ["business_entity_master.entity_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["candidate_entity_id"], ["business_entity_master.entity_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("suggestion_id"),
        sa.UniqueConstraint(
            "source_entity_id",
            "candidate_entity_id",
            "rule_used",
            name="uq_ces_source_candidate_rule",
        ),
    )
    op.create_index("ix_ces_status", "canonical_entity_suggestion", ["status"])
    op.create_index("ix_ces_score", "canonical_entity_suggestion", ["score"])


def downgrade() -> None:
    op.drop_index("ix_ces_score", table_name="canonical_entity_suggestion")
    op.drop_index("ix_ces_status", table_name="canonical_entity_suggestion")
    op.drop_table("canonical_entity_suggestion")
    op.drop_index("ix_ber_canonical_id", table_name="business_entity_resolution")
    op.drop_table("business_entity_resolution")
    op.drop_index("ix_cbe_primary_rfc", table_name="canonical_business_entity")
    op.drop_index("ix_cbe_normalized_name", table_name="canonical_business_entity")
    op.drop_table("canonical_business_entity")
