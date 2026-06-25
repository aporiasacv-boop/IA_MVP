from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.repositories.metadata_repository import MetadataRepository
from app.database.database import SessionLocal
from app.services.metadata_service import MetadataService
from app.services.temporal_resolver import TemporalResolver

BASE_URL = "http://127.0.0.1:8001"

TEMPORAL_CASES = [
    ("enero", "2025-01-01", "2025-01-31"),
    ("junio", "2025-06-01", "2025-06-30"),
    ("diciembre", "2025-12-01", "2025-12-31"),
    ("2025", "2025-01-01", "2025-12-31"),
]


def main() -> int:
    print("=" * 80)
    print("TEST METADATA LAYER - IA_MVP")
    print(f"Base URL: {BASE_URL}")
    print("=" * 80)

    errors = 0

    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        try:
            health = client.get("/health")
            if health.status_code != 200:
                print("[FAIL] Servidor no disponible en /health")
                return 1
        except httpx.ConnectError:
            print("[FAIL] No se pudo conectar. Ejecuta: uvicorn app.main:app --reload --port 8001")
            return 1

        started = time.perf_counter()
        response = client.get("/api/metadata")
        elapsed_ms = (time.perf_counter() - started) * 1000

        print("")
        print("GET /api/metadata")
        print(f"  HTTP: {response.status_code}")
        print(f"  Tiempo: {elapsed_ms:.2f} ms")

        if response.status_code != 200:
            print(f"  [FAIL] {response.text[:200]}")
            errors += 1
        else:
            metadata = response.json()
            print(f"  Metadata encontrada: {json.dumps(metadata, ensure_ascii=False)}")
            required = [
                "fecha_minima",
                "fecha_maxima",
                "registros",
                "clientes",
                "proveedores",
                "cuentas",
                "anios",
                "meses",
            ]
            missing = [field for field in required if field not in metadata]
            if missing:
                print(f"  [FAIL] Faltan campos: {missing}")
                errors += 1
            elif metadata["registros"] <= 0:
                print("  [FAIL] registros debe ser mayor a 0")
                errors += 1
            else:
                print("  [OK]")

    session = SessionLocal()
    try:
        summary = MetadataService(MetadataRepository(session)).get_dataset_summary()
        resolver = TemporalResolver.from_metadata(summary)

        print("")
        print("TemporalResolver")
        for expression, expected_start, expected_end in TEMPORAL_CASES:
            started = time.perf_counter()
            period = resolver.resolve(expression)
            elapsed_ms = (time.perf_counter() - started) * 1000
            print("")
            print(f"  Expresion: {expression}")
            print(f"  Tiempo: {elapsed_ms:.4f} ms")
            print(f"  Periodo resuelto: {period}")
            if period is None:
                print("  [FAIL] No se resolvio el periodo")
                errors += 1
            elif period["inicio"] != expected_start or period["fin"] != expected_end:
                print(
                    f"  [FAIL] Se esperaba {expected_start} a {expected_end}, "
                    f"obtenido {period['inicio']} a {period['fin']}"
                )
                errors += 1
            else:
                print("  [OK]")
    finally:
        session.close()

    print("")
    print("=" * 80)
    if errors:
        print(f"[FAIL] {errors} validacion(es) con error")
        return 1
    print("[OK] Metadata y contexto temporal validados correctamente")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
