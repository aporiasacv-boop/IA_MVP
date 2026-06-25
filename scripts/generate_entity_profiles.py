from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.business_entity_profile.profiler import EntityProfileGenerator
from app.business_entity_profile.repository import BusinessEntityProfileRepository
from app.database.database import SessionLocal


def main() -> int:
    print("Generando perfiles de comportamiento empresarial (idempotente)...")
    with SessionLocal() as session:
        repository = BusinessEntityProfileRepository(session)
        generator = EntityProfileGenerator(repository)
        result = generator.run_idempotent()
        print(f"  Perfiles procesados: {result.profiles_upserted}")
        print(f"  Creados: {result.profiles_created}")
        print(f"  Actualizados: {result.profiles_updated}")
        print(f"  Tiempo (s): {result.generation_time_seconds}")
    print("[OK] Generación de perfiles completada")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
