from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.business_entity_master.loader import BusinessEntityMasterLoader
from app.business_entity_master.repository import BusinessEntityMasterRepository
from app.database.database import SessionLocal


def main() -> int:
    csv_path = PROJECT_ROOT / "docs" / "entity_catalog_candidate.csv"
    print("Cargando catálogo maestro de entidades (idempotente)...")
    print(f"CSV opcional: {csv_path}")

    with SessionLocal() as session:
        loader = BusinessEntityMasterLoader(BusinessEntityMasterRepository(session))
        result = loader.load_idempotent(csv_path=csv_path if csv_path.exists() else None)
        print(f"  Insertadas: {result.inserted}")
        print(f"  Actualizadas: {result.updated}")
        print(f"  Total procesadas: {result.total_processed}")
        print(f"  Códigos duplicados cross-source: {result.duplicated_entity_codes}")
    print("[OK] Carga completada")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
