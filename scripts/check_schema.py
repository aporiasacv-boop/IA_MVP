from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import inspect, text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.settings import settings
from app.database.database import engine

EXPECTED_INDEXES = [
    "ix_movimientos_diario_fecha",
    "ix_movimientos_diario_mes",
    "ix_movimientos_diario_anio",
    "ix_movimientos_diario_account_display_value",
    "ix_movimientos_diario_cuenta_proveedor",
    "ix_movimientos_diario_cuenta_cliente",
    "ix_movimientos_diario_numero_diario",
]

TABLE_NAME = "movimientos_diario"


def print_section(title: str) -> None:
    print("")
    print("=" * 72)
    print(title)
    print("=" * 72)


def main() -> int:
    inspector = inspect(engine)

    print_section("CHECK SCHEMA - IA_MVP")
    print(f"Base: {settings.DATABASE_NAME}")
    print(f"Host: {settings.DATABASE_HOST}:{settings.DATABASE_PORT}")
    print(f"Usuario: {settings.DATABASE_USER}")

    with engine.connect() as connection:
        version = connection.execute(text("SELECT version()")).scalar()
        print(f"Version: {version.split(',')[0]}")

    tables = sorted(inspector.get_table_names())
    print_section("Tablas existentes")
    if not tables:
        print("(sin tablas)")
    for table in tables:
        print(f"  - {table}")

    if TABLE_NAME not in tables:
        print("")
        print(f"[FAIL] La tabla {TABLE_NAME} no existe")
        return 1

    print("")
    print(f"[OK] Tabla {TABLE_NAME} existe")

    print_section(f"Columnas de {TABLE_NAME}")
    columns = inspector.get_columns(TABLE_NAME)
    for column in columns:
        nullable = "NULL" if column.get("nullable") else "NOT NULL"
        print(f"  - {column['name']}: {column['type']} {nullable}")

    print_section(f"Indices de {TABLE_NAME}")
    indexes = inspector.get_indexes(TABLE_NAME)
    index_names = sorted(index["name"] for index in indexes if index.get("name"))
    if not index_names:
        print("(sin indices)")
    for index_name in index_names:
        print(f"  - {index_name}")

    missing_indexes = [name for name in EXPECTED_INDEXES if name not in index_names]
    extra_indexes = [name for name in index_names if name not in EXPECTED_INDEXES]

    print_section("Validacion de indices esperados")
    for index_name in EXPECTED_INDEXES:
        status = "[OK]" if index_name in index_names else "[FAIL]"
        print(f"  {status} {index_name}")

    if missing_indexes:
        print("")
        print(f"[FAIL] Indices faltantes: {', '.join(missing_indexes)}")
        return 1

    if extra_indexes:
        print("")
        print(f"[INFO] Indices adicionales: {', '.join(extra_indexes)}")

    print("")
    print("[OK] Esquema validado correctamente")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
