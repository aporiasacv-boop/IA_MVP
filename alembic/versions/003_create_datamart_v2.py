"""create temporal datamart v2 tables and materialized views

Revision ID: 003_create_datamart_v2
Revises: 002_create_datamart
Create Date: 2026-06-18 16:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003_create_datamart_v2"
down_revision: Union[str, None] = "002_create_datamart"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "fact_cliente_mes",
        sa.Column("anio", sa.Integer(), nullable=False),
        sa.Column("mes", sa.Integer(), nullable=False),
        sa.Column("cliente_codigo", sa.String(length=50), nullable=False),
        sa.Column("cliente_nombre", sa.String(length=255), nullable=False),
        sa.Column("movimientos", sa.Integer(), nullable=False),
        sa.Column("monto_total", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("monto_promedio", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("fecha_actualizacion", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("anio", "mes", "cliente_codigo"),
    )
    op.create_table(
        "fact_proveedor_mes",
        sa.Column("anio", sa.Integer(), nullable=False),
        sa.Column("mes", sa.Integer(), nullable=False),
        sa.Column("proveedor_codigo", sa.String(length=100), nullable=False),
        sa.Column("proveedor_nombre", sa.String(length=255), nullable=False),
        sa.Column("movimientos", sa.Integer(), nullable=False),
        sa.Column("monto_total", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("monto_promedio", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("fecha_actualizacion", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("anio", "mes", "proveedor_codigo"),
    )
    op.create_table(
        "fact_cuenta_mes",
        sa.Column("anio", sa.Integer(), nullable=False),
        sa.Column("mes", sa.Integer(), nullable=False),
        sa.Column("cuenta_codigo", sa.String(length=100), nullable=False),
        sa.Column("cuenta_nombre", sa.String(length=255), nullable=False),
        sa.Column("movimientos", sa.Integer(), nullable=False),
        sa.Column("monto_total", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("monto_promedio", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("fecha_actualizacion", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("anio", "mes", "cuenta_codigo"),
    )

    op.create_index("ix_fact_cliente_mes_anio_mes", "fact_cliente_mes", ["anio", "mes"], unique=False)
    op.create_index("ix_fact_cliente_mes_cliente_codigo", "fact_cliente_mes", ["cliente_codigo"], unique=False)
    op.create_index("ix_fact_proveedor_mes_anio_mes", "fact_proveedor_mes", ["anio", "mes"], unique=False)
    op.create_index("ix_fact_proveedor_mes_proveedor_codigo", "fact_proveedor_mes", ["proveedor_codigo"], unique=False)
    op.create_index("ix_fact_cuenta_mes_anio_mes", "fact_cuenta_mes", ["anio", "mes"], unique=False)
    op.create_index("ix_fact_cuenta_mes_cuenta_codigo", "fact_cuenta_mes", ["cuenta_codigo"], unique=False)

    op.execute(
        """
        CREATE MATERIALIZED VIEW mv_cliente_evolucion AS
        SELECT
            anio,
            mes,
            cliente_codigo,
            cliente_nombre,
            movimientos,
            monto_total,
            monto_promedio,
            fecha_actualizacion
        FROM fact_cliente_mes
        ORDER BY cliente_codigo, anio, mes
        """
    )
    op.execute(
        """
        CREATE MATERIALIZED VIEW mv_proveedor_evolucion AS
        SELECT
            anio,
            mes,
            proveedor_codigo,
            proveedor_nombre,
            movimientos,
            monto_total,
            monto_promedio,
            fecha_actualizacion
        FROM fact_proveedor_mes
        ORDER BY proveedor_codigo, anio, mes
        """
    )
    op.execute(
        """
        CREATE MATERIALIZED VIEW mv_cuenta_evolucion AS
        SELECT
            anio,
            mes,
            cuenta_codigo,
            cuenta_nombre,
            movimientos,
            monto_total,
            monto_promedio,
            fecha_actualizacion
        FROM fact_cuenta_mes
        ORDER BY cuenta_codigo, anio, mes
        """
    )


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_cuenta_evolucion")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_proveedor_evolucion")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_cliente_evolucion")
    op.drop_index("ix_fact_cuenta_mes_cuenta_codigo", table_name="fact_cuenta_mes")
    op.drop_index("ix_fact_cuenta_mes_anio_mes", table_name="fact_cuenta_mes")
    op.drop_index("ix_fact_proveedor_mes_proveedor_codigo", table_name="fact_proveedor_mes")
    op.drop_index("ix_fact_proveedor_mes_anio_mes", table_name="fact_proveedor_mes")
    op.drop_index("ix_fact_cliente_mes_cliente_codigo", table_name="fact_cliente_mes")
    op.drop_index("ix_fact_cliente_mes_anio_mes", table_name="fact_cliente_mes")
    op.drop_table("fact_cuenta_mes")
    op.drop_table("fact_proveedor_mes")
    op.drop_table("fact_cliente_mes")
