from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class FactMes(Base):
    __tablename__ = "fact_mes"

    anio: Mapped[int] = mapped_column(Integer, primary_key=True)
    mes: Mapped[int] = mapped_column(Integer, primary_key=True)
    movimientos: Mapped[int] = mapped_column(Integer, nullable=False)
    monto_total: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    monto_promedio: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)


class FactCuenta(Base):
    __tablename__ = "fact_cuenta"

    cuenta_codigo: Mapped[str] = mapped_column(String(100), primary_key=True)
    cuenta_nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    movimientos: Mapped[int] = mapped_column(Integer, nullable=False)
    monto_total: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    monto_promedio: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)


class FactCliente(Base):
    __tablename__ = "fact_cliente"

    cliente_codigo: Mapped[str] = mapped_column(String(50), primary_key=True)
    cliente_nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    movimientos: Mapped[int] = mapped_column(Integer, nullable=False)
    monto_total: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    monto_promedio: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)


class FactProveedor(Base):
    __tablename__ = "fact_proveedor"

    proveedor_codigo: Mapped[str] = mapped_column(String(100), primary_key=True)
    proveedor_nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    movimientos: Mapped[int] = mapped_column(Integer, nullable=False)
    monto_total: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    monto_promedio: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)


class FactDivisa(Base):
    __tablename__ = "fact_divisa"

    divisa: Mapped[str] = mapped_column(String(10), primary_key=True)
    movimientos: Mapped[int] = mapped_column(Integer, nullable=False)
    monto_total: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    monto_promedio: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)


class FactClienteMes(Base):
    __tablename__ = "fact_cliente_mes"

    anio: Mapped[int] = mapped_column(Integer, primary_key=True)
    mes: Mapped[int] = mapped_column(Integer, primary_key=True)
    cliente_codigo: Mapped[str] = mapped_column(String(50), primary_key=True)
    cliente_nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    movimientos: Mapped[int] = mapped_column(Integer, nullable=False)
    monto_total: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    monto_promedio: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)


class FactProveedorMes(Base):
    __tablename__ = "fact_proveedor_mes"

    anio: Mapped[int] = mapped_column(Integer, primary_key=True)
    mes: Mapped[int] = mapped_column(Integer, primary_key=True)
    proveedor_codigo: Mapped[str] = mapped_column(String(100), primary_key=True)
    proveedor_nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    movimientos: Mapped[int] = mapped_column(Integer, nullable=False)
    monto_total: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    monto_promedio: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)


class FactCuentaMes(Base):
    __tablename__ = "fact_cuenta_mes"

    anio: Mapped[int] = mapped_column(Integer, primary_key=True)
    mes: Mapped[int] = mapped_column(Integer, primary_key=True)
    cuenta_codigo: Mapped[str] = mapped_column(String(100), primary_key=True)
    cuenta_nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    movimientos: Mapped[int] = mapped_column(Integer, nullable=False)
    monto_total: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    monto_promedio: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
