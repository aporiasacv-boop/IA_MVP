from sqlalchemy import text
from sqlalchemy.orm import Session

from app.enterprise_knowledge.schemas import EnterpriseKnowledgeObjectSchema
from app.enterprise_reasoning.schemas import EnterpriseReasoningObjectSchema


class EvidencePackageRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def resolve_canonical_id(self, entity_hints: list[str]) -> int | None:
        for hint in entity_hints:
            token = hint.strip()
            if not token or len(token) < 3:
                continue
            row = self.session.execute(
                text(
                    """
                    SELECT canonical_id
                    FROM canonical_business_entity
                    WHERE UPPER(canonical_name) = UPPER(:name)
                       OR UPPER(normalized_name) = UPPER(:name)
                    LIMIT 1
                    """
                ),
                {"name": token},
            ).mappings().first()
            if row:
                return int(row["canonical_id"])
            row = self.session.execute(
                text(
                    """
                    SELECT canonical_id
                    FROM canonical_business_entity
                    WHERE canonical_name ILIKE :pattern OR normalized_name ILIKE :pattern
                    LIMIT 1
                    """
                ),
                {"pattern": f"%{token}%"},
            ).mappings().first()
            if row:
                return int(row["canonical_id"])
        return None

    def fetch_eko(self, canonical_id: int) -> EnterpriseKnowledgeObjectSchema | None:
        row = self.session.execute(
            text("SELECT knowledge_payload FROM enterprise_knowledge_object WHERE canonical_id = :id"),
            {"id": canonical_id},
        ).mappings().first()
        if not row:
            return None
        return EnterpriseKnowledgeObjectSchema.model_validate(row["knowledge_payload"])

    def fetch_ero(self, canonical_id: int) -> EnterpriseReasoningObjectSchema | None:
        row = self.session.execute(
            text("SELECT reasoning_payload FROM enterprise_reasoning_object WHERE canonical_id = :id"),
            {"id": canonical_id},
        ).mappings().first()
        if not row:
            return None
        return EnterpriseReasoningObjectSchema.model_validate(row["reasoning_payload"])

    def fetch_first_available_entity(self) -> int | None:
        row = self.session.execute(
            text(
                """
                SELECT eko.canonical_id
                FROM enterprise_knowledge_object eko
                ORDER BY eko.completeness DESC
                LIMIT 1
                """
            )
        ).mappings().first()
        return int(row["canonical_id"]) if row else None
