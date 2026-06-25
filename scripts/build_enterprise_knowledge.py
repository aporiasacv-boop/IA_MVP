from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database.database import SessionLocal
from app.enterprise_knowledge.repository import EnterpriseKnowledgeRepository
from app.enterprise_knowledge.service import EnterpriseKnowledgeService


def main() -> int:
    print("Construyendo Enterprise Knowledge Objects (idempotente)...")
    with SessionLocal() as session:
        repository = EnterpriseKnowledgeRepository(session)
        service = EnterpriseKnowledgeService(repository)
        result = service.run_build()
        print(f"  Entidades procesadas: {result.entities_processed}")
        print(f"  Objetos creados: {result.objects_created}")
        print(f"  Objetos actualizados: {result.objects_updated}")
        print(f"  Tiempo (s): {result.build_time_seconds}")
    print("[OK] Construcción de EKO completada")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
