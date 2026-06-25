"""create datamart fact tables and materialized views

Revision ID: 002_create_datamart
Revises: 001_movimientos_diario
Create Date: 2026-06-18 14:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_create_datamart"
down_revision: Union[str, None] = "001_movimientos_diario"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "fact_mes",
        sa.Column("anio", sa.Integer(), nullable=False),
        sa.Column("mes", sa.Integer(), nullable=False),
        sa.Column("movimientos", sa.Integer(), nullable=False),
        sa.Column("monto_total", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("monto_promedio", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("fecha_actualizacion", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("anio", "mes"),
    )
    op.create_table(
        "fact_cuenta",
        sa.Column("cuenta_codigo", sa.String(length=100), nullable=False),
        sa.Column("cuenta_nombre", sa.String(length=255), nullable=False),
        sa.Column("movimientos", sa.Integer(), nullable=False),
        sa.Column("monto_total", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("monto_promedio", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("fecha_actualizacion", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("cuenta_codigo"),
    )
    op.create_table(
        "fact_cliente",
        sa.Column("cliente_codigo", sa.String(length=50), nullable=False),
        sa.Column("cliente_nombre", sa.String(length=255), nullable=False),
        sa.Column("movimientos", sa.Integer(), nullable=False),
        sa.Column("monto_total", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("monto_promedio", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("fecha_actualizacion", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("cliente_codigo"),
    )
    op.create_table(
        "fact_proveedor",
        sa.Column("proveedor_codigo", sa.String(length=100), nullable=False),
        sa.Column("proveedor_nombre", sa.String(length=255), nullable=False),
        sa.Column("movimientos", sa.Integer(), nullable=False),
        sa.Column("monto_total", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("monto_promedio", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("fecha_actualizacion", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("proveedor_codigo"),
    )
    op.create_table(
        "fact_divisa",
        sa.Column("divisa", sa.String(length=10), nullable=False),
        sa.Column("movimientos", sa.Integer(), nullable=False),
        sa.Column("monto_total", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("monto_promedio", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("fecha_actualizacion", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("divisa"),
    )

    op.create_index("ix_fact_mes_anio_mes", "fact_mes", ["anio", "mes"], unique=False)
    op.create_index("ix_fact_cuenta_movimientos", "fact_cuenta", ["movimientos"], unique=False)
    op.create_index("ix_fact_cliente_movimientos", "fact_cliente", ["movimientos"], unique=False)
    op.create_index("ix_fact_proveedor_movimientos", "fact_proveedor", ["movimientos"], unique=False)

    op.execute(
        """
        CREATE MATERIALIZED VIEW mv_resumen_mensual AS
        SELECT
            anio,
            mes,
            movimientos,
            monto_total,
            monto_promedio,
            fecha_actualizacion
        FROM fact_mes
        ORDER BY anio, mes
        """
    )
    op.execute(
        """
        CREATE MATERIALIZED VIEW mv_top_cuentas AS
        SELECT
            ROW_NUMBER() OVER (ORDER BY movimientos DESC, ABS(monto_total) DESC) AS ranking,
            cuenta_codigo,
            cuenta_nombre,
            movimientos,
            monto_total,
            monto_promedio,
            fecha_actualizacion
        FROM fact_cuenta
        """
    )
    op.execute(
        """
        CREATE MATERIALIZED VIEW mv_top_clientes AS
        SELECT
            ROW_NUMBER() OVER (ORDER BY movimientos DESC, ABS(monto_total) DESC) AS ranking,
            cliente_codigo,
            cliente_nombre,
            movimientos,
            monto_total,
            monto_promedio,
            fecha_actualizacion
        FROM fact_cliente
        """
    )
    op.execute(
        """
        CREATE MATERIALIZED VIEW mv_top_proveedores AS
        SELECT
            ROW_NUMBER() OVER (ORDER BY movimientos DESC, ABS(monto_total) DESC) AS ranking,
            proveedor_codigo,
            proveedor_nombre,
            movimientos,
            monto_total,
            monto_promedio,
            fecha_actualizacion
        FROM fact_proveedor
        """
    )


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_top_proveedores")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_top_clientes")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_top_cuentas")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_resumen_mensual")
    op.drop_index("ix_fact_proveedor_movimientos", table_name="fact_proveedor")
    op.drop_index("ix_fact_cliente_movimientos", table_name="fact_cliente")
    op.drop_index("ix_fact_cuenta_movimientos", table_name="fact_cuenta")
    op.drop_index("ix_fact_mes_anio_mes", table_name="fact_mes")
    op.drop_table("fact_divisa")
    op.drop_table("fact_proveedor")
    op.drop_table("fact_cliente")
    op.drop_table("fact_cuenta")
    op.drop_table("fact_mes")
