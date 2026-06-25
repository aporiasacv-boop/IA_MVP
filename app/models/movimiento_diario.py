from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Date, DateTime, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class MovimientoDiario(Base):
    __tablename__ = "movimientos_diario"
    __table_args__ = (
        Index("ix_movimientos_diario_fecha", "fecha"),
        Index("ix_movimientos_diario_mes", "mes"),
        Index("ix_movimientos_diario_anio", "anio"),
        Index("ix_movimientos_diario_account_display_value", "account_display_value"),
        Index("ix_movimientos_diario_cuenta_proveedor", "cuenta_proveedor"),
        Index("ix_movimientos_diario_cuenta_cliente", "cuenta_cliente"),
        Index("ix_movimientos_diario_numero_diario", "numero_diario"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    hoja_origen: Mapped[str] = mapped_column(String(20), nullable=False)
    numero_diario: Mapped[str] = mapped_column(String(50), nullable=False)
    asiento: Mapped[str] = mapped_column(String(50), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    anio_cerrado: Mapped[str] = mapped_column(String(10), nullable=False)
    account_display_value: Mapped[str] = mapped_column(String(100), nullable=False)
    nombre_cuenta: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    divisa: Mapped[str] = mapped_column(String(10), nullable=False)
    monto_divisa_transaccion: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    monto: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    monto_divisa_reporte: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    tipo_registro: Mapped[str | None] = mapped_column(String(100), nullable=True)
    capa_registro: Mapped[str] = mapped_column(String(50), nullable=False)
    cuenta_proveedor: Mapped[str | None] = mapped_column(String(100), nullable=True)
    nombre_proveedor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cuenta_cliente: Mapped[str | None] = mapped_column(String(50), nullable=True)
    nombre_cliente: Mapped[str | None] = mapped_column(String(255), nullable=True)
    creado_por: Mapped[str] = mapped_column(String(100), nullable=False)
    creado_por2: Mapped[str] = mapped_column(String(100), nullable=False)
    fecha_carga: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    hash_fuente: Mapped[str] = mapped_column(String(64), nullable=False)
