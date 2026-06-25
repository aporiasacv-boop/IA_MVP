from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.canonical_business_entity.repository import CanonicalBusinessEntityRepository
from app.canonical_business_entity.suggestion_engine import CanonicalSuggestionEngine
from app.database.database import SessionLocal


def main() -> int:
    print("Generando identidades canónicas y sugerencias (idempotente)...")
    with SessionLocal() as session:
        repository = CanonicalBusinessEntityRepository(session)
        engine = CanonicalSuggestionEngine(repository)
        result = engine.run_idempotent()
        print(f"  Singletons creados: {result.singletons_created}")
        print(f"  Resoluciones creadas: {result.resolutions_created}")
        print(f"  Sugerencias insertadas: {result.suggestions_inserted}")
        print(f"  Sugerencias actualizadas: {result.suggestions_updated}")
    print("[OK] Proceso canónico completado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
