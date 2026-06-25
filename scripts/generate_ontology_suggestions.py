from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.business_ontology.ontology_engine import OntologyEngine
from app.business_ontology.repository import BusinessOntologyRepository
from app.database.database import SessionLocal


def main() -> int:
    print("Generando sugerencias de ontología empresarial (idempotente)...")
    with SessionLocal() as session:
        repository = BusinessOntologyRepository(session)
        engine = OntologyEngine(repository)
        result = engine.run_idempotent()
        print(f"  Tipos sembrados: {result.types_seeded}")
        print(f"  Reglas sembradas: {result.rules_seeded}")
        print(f"  Entidades procesadas: {result.entities_processed}")
        print(f"  Sugerencias insertadas: {result.suggestions_inserted}")
        print(f"  Sugerencias actualizadas: {result.suggestions_updated}")
        print(f"  Tiempo (s): {result.generation_time_seconds}")
    print("[OK] Generación de ontología completada")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
