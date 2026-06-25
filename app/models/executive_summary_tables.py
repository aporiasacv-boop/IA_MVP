from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class ClienteResumen(Base):
    __tablename__ = "cliente_resumen"

    cliente_codigo: Mapped[str] = mapped_column(String(50), primary_key=True)
    cliente_nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    movimientos: Mapped[int] = mapped_column(Integer, nullable=False)
    monto_total: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    monto_promedio: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    participacion_pct: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    ranking: Mapped[int] = mapped_column(Integer, nullable=False)
    primer_movimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    ultimo_movimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)


class ProveedorResumen(Base):
    __tablename__ = "proveedor_resumen"

    proveedor_codigo: Mapped[str] = mapped_column(String(100), primary_key=True)
    proveedor_nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    movimientos: Mapped[int] = mapped_column(Integer, nullable=False)
    monto_total: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    monto_promedio: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    participacion_pct: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    ranking: Mapped[int] = mapped_column(Integer, nullable=False)
    primer_movimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    ultimo_movimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)


class CuentaResumen(Base):
    __tablename__ = "cuenta_resumen"

    cuenta_codigo: Mapped[str] = mapped_column(String(100), primary_key=True)
    cuenta_nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    movimientos: Mapped[int] = mapped_column(Integer, nullable=False)
    monto_total: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    monto_promedio: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    participacion_pct: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    ranking: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)


class MesResumen(Base):
    __tablename__ = "mes_resumen"

    anio: Mapped[int] = mapped_column(Integer, primary_key=True)
    mes: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre_mes: Mapped[str] = mapped_column(String(20), nullable=False)
    movimientos: Mapped[int] = mapped_column(Integer, nullable=False)
    monto_total: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    monto_promedio: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    participacion_pct: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    ranking_actividad: Mapped[int] = mapped_column(Integer, nullable=False)
    ranking_volumen: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
