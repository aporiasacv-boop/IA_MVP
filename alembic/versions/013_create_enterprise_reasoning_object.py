"""create enterprise reasoning object table

Revision ID: 013_create_enterprise_reasoning_object
Revises: 012_create_enterprise_knowledge_object
Create Date: 2026-06-24 20:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "013_create_enterprise_reasoning_object"
down_revision: Union[str, None] = "012_create_enterprise_knowledge_object"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "enterprise_reasoning_object",
        sa.Column("reasoning_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("canonical_id", sa.BigInteger(), nullable=False),
        sa.Column("reasoning_payload", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("average_confidence", sa.Numeric(precision=5, scale=4), nullable=False, server_default="0"),
        sa.Column("findings_count", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("alerts_count", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("recommendations_count", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("built_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["canonical_id"], ["canonical_business_entity.canonical_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("reasoning_id"),
        sa.UniqueConstraint("canonical_id", name="uq_ero_canonical_id"),
    )
    op.create_index("ix_ero_average_confidence", "enterprise_reasoning_object", ["average_confidence"])
    op.create_index("ix_ero_findings_count", "enterprise_reasoning_object", ["findings_count"])
    op.create_index("ix_ero_built_at", "enterprise_reasoning_object", ["built_at"])


def downgrade() -> None:
    op.drop_index("ix_ero_built_at", table_name="enterprise_reasoning_object")
    op.drop_index("ix_ero_findings_count", table_name="enterprise_reasoning_object")
    op.drop_index("ix_ero_average_confidence", table_name="enterprise_reasoning_object")
    op.drop_table("enterprise_reasoning_object")
