from __future__ import annotations

import sys
from pathlib import Path

import psycopg2
from psycopg2 import OperationalError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.settings import settings


def main() -> int:
    env_path = PROJECT_ROOT / ".env"
    env_source = ".env" if env_path.exists() else "settings.py (defaults, .env no encontrado)"

    print("Probando conexion PostgreSQL...")
    print(f"Configuracion: {env_source}")
    print(
        f"Host: {settings.DATABASE_HOST} | "
        f"Puerto: {settings.DATABASE_PORT} | "
        f"Usuario: {settings.DATABASE_USER} | "
        f"Base: {settings.DATABASE_NAME}"
    )
    print("")

    try:
        connection = psycopg2.connect(
            host=settings.DATABASE_HOST,
            port=settings.DATABASE_PORT,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD,
            dbname=settings.DATABASE_NAME,
            connect_timeout=5,
        )
    except OperationalError as error:
        print("[FAIL] Conexion rechazada")
        print(str(error).strip())
        return 1

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            cursor.execute("SELECT current_database(), current_user")
            database_name, current_user = cursor.fetchone()
    finally:
        connection.close()

    print("[OK] Conexion exitosa")
    print(f"Base: {database_name}")
    print(f"Usuario: {current_user}")
    print(f"Version: {version.split(',')[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
