import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.database.database import SessionLocal
from app.enterprise_reasoning.repository import EnterpriseReasoningRepository
from app.enterprise_reasoning.service import EnterpriseReasoningService


def main() -> int:
    with SessionLocal() as session:
        repository = EnterpriseReasoningRepository(session)
        service = EnterpriseReasoningService(repository)
        result = service.run_build()
    print(
        f"ERO build: processed={result.entities_processed} "
        f"created={result.objects_created} updated={result.objects_updated} "
        f"rules_executed={result.rules_executed} time={result.build_time_seconds}s"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
