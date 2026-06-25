"""create executive summary tables

Revision ID: 004_create_executive_summaries
Revises: 003_create_datamart_v2
Create Date: 2026-06-18 18:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004_create_executive_summaries"
down_revision: Union[str, None] = "003_create_datamart_v2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cliente_resumen",
        sa.Column("cliente_codigo", sa.String(length=50), nullable=False),
        sa.Column("cliente_nombre", sa.String(length=255), nullable=False),
        sa.Column("movimientos", sa.Integer(), nullable=False),
        sa.Column("monto_total", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("monto_promedio", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("participacion_pct", sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column("ranking", sa.Integer(), nullable=False),
        sa.Column("primer_movimiento", sa.Date(), nullable=True),
        sa.Column("ultimo_movimiento", sa.Date(), nullable=True),
        sa.Column("fecha_actualizacion", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("cliente_codigo"),
    )
    op.create_table(
        "proveedor_resumen",
        sa.Column("proveedor_codigo", sa.String(length=100), nullable=False),
        sa.Column("proveedor_nombre", sa.String(length=255), nullable=False),
        sa.Column("movimientos", sa.Integer(), nullable=False),
        sa.Column("monto_total", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("monto_promedio", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("participacion_pct", sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column("ranking", sa.Integer(), nullable=False),
        sa.Column("primer_movimiento", sa.Date(), nullable=True),
        sa.Column("ultimo_movimiento", sa.Date(), nullable=True),
        sa.Column("fecha_actualizacion", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("proveedor_codigo"),
    )
    op.create_table(
        "cuenta_resumen",
        sa.Column("cuenta_codigo", sa.String(length=100), nullable=False),
        sa.Column("cuenta_nombre", sa.String(length=255), nullable=False),
        sa.Column("movimientos", sa.Integer(), nullable=False),
        sa.Column("monto_total", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("monto_promedio", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("participacion_pct", sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column("ranking", sa.Integer(), nullable=False),
        sa.Column("fecha_actualizacion", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("cuenta_codigo"),
    )
    op.create_table(
        "mes_resumen",
        sa.Column("anio", sa.Integer(), nullable=False),
        sa.Column("mes", sa.Integer(), nullable=False),
        sa.Column("nombre_mes", sa.String(length=20), nullable=False),
        sa.Column("movimientos", sa.Integer(), nullable=False),
        sa.Column("monto_total", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("monto_promedio", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("participacion_pct", sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column("ranking_actividad", sa.Integer(), nullable=False),
        sa.Column("ranking_volumen", sa.Integer(), nullable=False),
        sa.Column("fecha_actualizacion", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("anio", "mes"),
    )

    op.create_index("ix_cliente_resumen_ranking", "cliente_resumen", ["ranking"], unique=False)
    op.create_index("ix_proveedor_resumen_ranking", "proveedor_resumen", ["ranking"], unique=False)
    op.create_index("ix_cuenta_resumen_ranking", "cuenta_resumen", ["ranking"], unique=False)
    op.create_index("ix_mes_resumen_ranking_actividad", "mes_resumen", ["ranking_actividad"], unique=False)
    op.create_index("ix_mes_resumen_ranking_volumen", "mes_resumen", ["ranking_volumen"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_mes_resumen_ranking_volumen", table_name="mes_resumen")
    op.drop_index("ix_mes_resumen_ranking_actividad", table_name="mes_resumen")
    op.drop_index("ix_cuenta_resumen_ranking", table_name="cuenta_resumen")
    op.drop_index("ix_proveedor_resumen_ranking", table_name="proveedor_resumen")
    op.drop_index("ix_cliente_resumen_ranking", table_name="cliente_resumen")
    op.drop_table("mes_resumen")
    op.drop_table("cuenta_resumen")
    op.drop_table("proveedor_resumen")
    op.drop_table("cliente_resumen")
