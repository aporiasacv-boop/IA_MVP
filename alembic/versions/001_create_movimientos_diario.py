"""create movimientos_diario table

Revision ID: 001_movimientos_diario
Revises:
Create Date: 2026-06-18 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_movimientos_diario"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "movimientos_diario",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("hoja_origen", sa.String(length=20), nullable=False),
        sa.Column("numero_diario", sa.String(length=50), nullable=False),
        sa.Column("asiento", sa.String(length=50), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("mes", sa.Integer(), nullable=False),
        sa.Column("anio", sa.Integer(), nullable=False),
        sa.Column("anio_cerrado", sa.String(length=10), nullable=False),
        sa.Column("account_display_value", sa.String(length=100), nullable=False),
        sa.Column("nombre_cuenta", sa.String(length=255), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("divisa", sa.String(length=10), nullable=False),
        sa.Column("monto_divisa_transaccion", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("monto", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("monto_divisa_reporte", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("tipo_registro", sa.String(length=100), nullable=True),
        sa.Column("capa_registro", sa.String(length=50), nullable=False),
        sa.Column("cuenta_proveedor", sa.String(length=100), nullable=True),
        sa.Column("nombre_proveedor", sa.String(length=255), nullable=True),
        sa.Column("cuenta_cliente", sa.String(length=50), nullable=True),
        sa.Column("nombre_cliente", sa.String(length=255), nullable=True),
        sa.Column("creado_por", sa.String(length=100), nullable=False),
        sa.Column("creado_por2", sa.String(length=100), nullable=False),
        sa.Column("fecha_carga", sa.DateTime(), nullable=False),
        sa.Column("hash_fuente", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_movimientos_diario_fecha",
        "movimientos_diario",
        ["fecha"],
        unique=False,
    )
    op.create_index(
        "ix_movimientos_diario_mes",
        "movimientos_diario",
        ["mes"],
        unique=False,
    )
    op.create_index(
        "ix_movimientos_diario_anio",
        "movimientos_diario",
        ["anio"],
        unique=False,
    )
    op.create_index(
        "ix_movimientos_diario_account_display_value",
        "movimientos_diario",
        ["account_display_value"],
        unique=False,
    )
    op.create_index(
        "ix_movimientos_diario_cuenta_proveedor",
        "movimientos_diario",
        ["cuenta_proveedor"],
        unique=False,
    )
    op.create_index(
        "ix_movimientos_diario_cuenta_cliente",
        "movimientos_diario",
        ["cuenta_cliente"],
        unique=False,
    )
    op.create_index(
        "ix_movimientos_diario_numero_diario",
        "movimientos_diario",
        ["numero_diario"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_movimientos_diario_numero_diario", table_name="movimientos_diario")
    op.drop_index("ix_movimientos_diario_cuenta_cliente", table_name="movimientos_diario")
    op.drop_index("ix_movimientos_diario_cuenta_proveedor", table_name="movimientos_diario")
    op.drop_index("ix_movimientos_diario_account_display_value", table_name="movimientos_diario")
    op.drop_index("ix_movimientos_diario_anio", table_name="movimientos_diario")
    op.drop_index("ix_movimientos_diario_mes", table_name="movimientos_diario")
    op.drop_index("ix_movimientos_diario_fecha", table_name="movimientos_diario")
    op.drop_table("movimientos_diario")
