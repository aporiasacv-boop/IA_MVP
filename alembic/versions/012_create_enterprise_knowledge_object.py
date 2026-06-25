"""create enterprise knowledge object table

Revision ID: 012_create_enterprise_knowledge_object
Revises: 011_create_business_ontology
Create Date: 2026-06-24 18:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "012_create_enterprise_knowledge_object"
down_revision: Union[str, None] = "011_create_business_ontology"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "enterprise_knowledge_object",
        sa.Column("knowledge_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("canonical_id", sa.BigInteger(), nullable=False),
        sa.Column("knowledge_payload", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("completeness", sa.Numeric(precision=5, scale=4), nullable=False, server_default="0"),
        sa.Column("average_confidence", sa.Numeric(precision=5, scale=4), nullable=False, server_default="0"),
        sa.Column("built_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["canonical_id"], ["canonical_business_entity.canonical_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("knowledge_id"),
        sa.UniqueConstraint("canonical_id", name="uq_eko_canonical_id"),
    )
    op.create_index("ix_eko_completeness", "enterprise_knowledge_object", ["completeness"])
    op.create_index("ix_eko_average_confidence", "enterprise_knowledge_object", ["average_confidence"])
    op.create_index("ix_eko_built_at", "enterprise_knowledge_object", ["built_at"])


def downgrade() -> None:
    op.drop_index("ix_eko_built_at", table_name="enterprise_knowledge_object")
    op.drop_index("ix_eko_average_confidence", table_name="enterprise_knowledge_object")
    op.drop_index("ix_eko_completeness", table_name="enterprise_knowledge_object")
    op.drop_table("enterprise_knowledge_object")
