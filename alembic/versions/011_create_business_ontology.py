"""create business ontology tables

Revision ID: 011_create_business_ontology
Revises: 010_create_business_entity_profile
Create Date: 2026-06-24 16:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "011_create_business_ontology"
down_revision: Union[str, None] = "010_create_business_entity_profile"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "business_ontology_type",
        sa.Column("type_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("concept_category", sa.String(length=20), nullable=False),
        sa.Column("type_code", sa.String(length=60), nullable=False),
        sa.Column("type_label", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("type_id"),
        sa.UniqueConstraint("concept_category", "type_code", name="uq_bot_category_code"),
    )
    op.create_index("ix_bot_concept_category", "business_ontology_type", ["concept_category"])

    op.create_table(
        "business_ontology_rule",
        sa.Column("rule_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("rule_code", sa.String(length=80), nullable=False),
        sa.Column("concept_category", sa.String(length=20), nullable=False),
        sa.Column("target_type_id", sa.BigInteger(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("conditions_json", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("score_weight", sa.Numeric(precision=5, scale=4), nullable=False, server_default="0.8000"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["target_type_id"], ["business_ontology_type.type_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("rule_id"),
        sa.UniqueConstraint("rule_code", name="uq_bor_rule_code"),
    )
    op.create_index("ix_bor_concept_category", "business_ontology_rule", ["concept_category"])

    op.create_table(
        "business_ontology_assignment",
        sa.Column("assignment_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("canonical_id", sa.BigInteger(), nullable=False),
        sa.Column("concept_category", sa.String(length=20), nullable=False),
        sa.Column("type_id", sa.BigInteger(), nullable=False),
        sa.Column("rule_code", sa.String(length=80), nullable=False),
        sa.Column("evidence_json", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("score", sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column("confidence", sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["canonical_id"], ["canonical_business_entity.canonical_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["type_id"], ["business_ontology_type.type_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("assignment_id"),
        sa.UniqueConstraint(
            "canonical_id",
            "concept_category",
            "type_id",
            "rule_code",
            name="uq_boa_canonical_category_type_rule",
        ),
    )
    op.create_index("ix_boa_status", "business_ontology_assignment", ["status"])
    op.create_index("ix_boa_canonical_id", "business_ontology_assignment", ["canonical_id"])
    op.create_index("ix_boa_concept_category", "business_ontology_assignment", ["concept_category"])


def downgrade() -> None:
    op.drop_index("ix_boa_concept_category", table_name="business_ontology_assignment")
    op.drop_index("ix_boa_canonical_id", table_name="business_ontology_assignment")
    op.drop_index("ix_boa_status", table_name="business_ontology_assignment")
    op.drop_table("business_ontology_assignment")
    op.drop_index("ix_bor_concept_category", table_name="business_ontology_rule")
    op.drop_table("business_ontology_rule")
    op.drop_index("ix_bot_concept_category", table_name="business_ontology_type")
    op.drop_table("business_ontology_type")
