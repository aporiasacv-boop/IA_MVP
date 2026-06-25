from __future__ import annotations

import csv
import re
from datetime import datetime
from pathlib import Path

from app.business_entity_master.constants import (
    CLASSIFICATION_PENDING,
    SOURCE_COLUMN_ACCOUNT,
    SOURCE_COLUMN_CUSTOMER,
    SOURCE_COLUMN_VENDOR,
    SOURCE_SYSTEM_D365,
    SOURCE_TABLE_MOVIMIENTOS,
)
from app.business_entity_master.metrics import BusinessEntityMasterMetrics
from app.business_entity_master.repository import BusinessEntityMasterRepository
from app.business_entity_master.schemas import EntityLoadResult


_SOURCE_PATTERN = re.compile(r"Fuentes:\s*([a-z_]+)", re.IGNORECASE)

_SOURCE_MAP = {
    "cuenta_contable": SOURCE_COLUMN_ACCOUNT,
    "proveedor_dim": SOURCE_COLUMN_VENDOR,
    "cliente_dim": SOURCE_COLUMN_CUSTOMER,
}


class BusinessEntityMasterLoader:
    def __init__(self, repository: BusinessEntityMasterRepository) -> None:
        self._repository = repository

    def load_from_movimientos(self, *, now: datetime | None = None) -> EntityLoadResult:
        timestamp = now or datetime.now()
        discovered = self._repository.fetch_discovered_entities()
        return self._upsert_batch(discovered, timestamp=timestamp)

    def load_from_csv(
        self,
        csv_path: Path,
        *,
        now: datetime | None = None,
    ) -> EntityLoadResult:
        timestamp = now or datetime.now()
        rows: list[dict] = []
        with csv_path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                source_column = self._resolve_source_column(row.get("observaciones", ""))
                if source_column is None:
                    continue
                rows.append(
                    {
                        "entity_code": str(row["codigo"]).strip(),
                        "entity_name": str(row["nombre"]).strip(),
                        "source_column": source_column,
                        "movement_count": int(row["cantidad_movimientos"]),
                        "movement_amount": row["monto_total"],
                        "first_seen": None,
                        "last_seen": None,
                        "confidence": str(row.get("confianza") or "").strip() or None,
                    }
                )
        return self._upsert_batch(rows, timestamp=timestamp)

    def load_idempotent(
        self,
        *,
        csv_path: Path | None = None,
        now: datetime | None = None,
    ) -> EntityLoadResult:
        """Carga autoritativa desde SQL; CSV opcional enriquece confidence."""
        timestamp = now or datetime.now()
        sql_result = self.load_from_movimientos(now=timestamp)
        if csv_path is not None and csv_path.exists():
            self._merge_csv_confidence(csv_path, timestamp=timestamp)
        total = self._repository.count_all()
        duplicated = self._repository.count_duplicated_codes()
        BusinessEntityMasterMetrics.record_refresh(
            loaded=sql_result.total_processed,
            duplicated=duplicated,
            refreshed_at=timestamp,
        )
        return EntityLoadResult(
            inserted=sql_result.inserted,
            updated=sql_result.updated,
            total_processed=sql_result.total_processed,
            duplicated_entity_codes=duplicated,
        )

    def _merge_csv_confidence(self, csv_path: Path, *, timestamp: datetime) -> None:
        with csv_path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                source_column = self._resolve_source_column(row.get("observaciones", ""))
                if source_column is None:
                    continue
                confidence = str(row.get("confianza") or "").strip() or None
                if confidence is None:
                    continue
                matches = self._repository.get_by_code(
                    str(row["codigo"]).strip(),
                    source_column=source_column,
                )
                for entity in matches:
                    entity.confidence = confidence
                    entity.updated_at = timestamp
        self._repository.session.commit()

    def _upsert_batch(self, rows: list[dict], *, timestamp: datetime) -> EntityLoadResult:
        inserted = 0
        updated = 0
        for row in rows:
            entity_name = str(row.get("entity_name") or row["entity_code"]).strip()
            _, is_new = self._repository.upsert_entity(
                entity_code=str(row["entity_code"]).strip(),
                entity_name=entity_name,
                source_system=SOURCE_SYSTEM_D365,
                source_table=SOURCE_TABLE_MOVIMIENTOS,
                source_column=str(row["source_column"]),
                movement_count=int(row["movement_count"]),
                movement_amount=row["movement_amount"],
                first_seen=row.get("first_seen"),
                last_seen=row.get("last_seen"),
                classification_status=CLASSIFICATION_PENDING,
                confidence=row.get("confidence"),
                now=timestamp,
            )
            if is_new:
                inserted += 1
            else:
                updated += 1
        self._repository.session.commit()
        return EntityLoadResult(
            inserted=inserted,
            updated=updated,
            total_processed=inserted + updated,
            duplicated_entity_codes=self._repository.count_duplicated_codes(),
        )

    @staticmethod
    def _resolve_source_column(observaciones: str) -> str | None:
        match = _SOURCE_PATTERN.search(observaciones or "")
        if not match:
            return None
        return _SOURCE_MAP.get(match.group(1).lower())
