"""create business_entity_master table

Revision ID: 008_create_business_entity_master
Revises: 007_add_business_analytics_columns
Create Date: 2026-06-23 18:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "008_create_business_entity_master"
down_revision: Union[str, None] = "007_add_business_analytics_columns"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "business_entity_master",
        sa.Column("entity_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("entity_code", sa.String(length=100), nullable=False),
        sa.Column("entity_name", sa.String(length=255), nullable=False),
        sa.Column("source_system", sa.String(length=50), nullable=False),
        sa.Column("source_table", sa.String(length=100), nullable=False),
        sa.Column("source_column", sa.String(length=100), nullable=False),
        sa.Column("movement_count", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("movement_amount", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0"),
        sa.Column("first_seen", sa.Date(), nullable=True),
        sa.Column("last_seen", sa.Date(), nullable=True),
        sa.Column("classification_status", sa.String(length=30), nullable=False, server_default="pending"),
        sa.Column("confidence", sa.String(length=30), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("entity_id"),
        sa.UniqueConstraint(
            "source_system",
            "source_table",
            "source_column",
            "entity_code",
            name="uq_business_entity_source_code",
        ),
    )
    op.create_index("ix_bem_entity_code", "business_entity_master", ["entity_code"], unique=False)
    op.create_index(
        "ix_bem_classification_status",
        "business_entity_master",
        ["classification_status"],
        unique=False,
    )
    op.create_index("ix_bem_source_column", "business_entity_master", ["source_column"], unique=False)
    op.create_index("ix_bem_movement_count", "business_entity_master", ["movement_count"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_bem_movement_count", table_name="business_entity_master")
    op.drop_index("ix_bem_source_column", table_name="business_entity_master")
    op.drop_index("ix_bem_classification_status", table_name="business_entity_master")
    op.drop_index("ix_bem_entity_code", table_name="business_entity_master")
    op.drop_table("business_entity_master")
