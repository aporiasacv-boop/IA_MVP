import uuid

from app.query_engine.business_query import BusinessQuery
from app.query_engine.query_types import BusinessQueryType
from app.schemas.semantic_intent import BusinessSemanticIntent
from app.slot_clarification.required_slots import (
    FILTER_KEY_BY_SLOT,
    REQUIRED_SLOTS_BY_QUERY_TYPE,
)
from app.slot_clarification.schemas import SlotClarificationResult
from app.slot_clarification.slots import ClarificationSlot
from app.slot_clarification.templates import SLOT_CLARIFICATION_TEMPLATES


class SlotClarificationEngine:
    """Detecta filtros obligatorios faltantes y solicita un único dato por turno."""

    def resolve(
        self,
        semantic_intent: BusinessSemanticIntent,
        business_query: BusinessQuery,
    ) -> SlotClarificationResult | None:
        query_type = business_query.query_type
        if query_type not in REQUIRED_SLOTS_BY_QUERY_TYPE:
            return None

        missing_slots = self._find_missing_slots(
            query_type,
            business_query.filters,
            semantic_intent,
        )
        if not missing_slots:
            return None

        primary_slot = missing_slots[0]
        return SlotClarificationResult(
            success=True,
            answer=SLOT_CLARIFICATION_TEMPLATES[primary_slot],
            pending_query_type=query_type.value,
            missing_slots=[slot.value for slot in missing_slots],
            session_token=uuid.uuid4().hex,
            metadata={
                "clarification_type": "missing_slot",
                "confidence": semantic_intent.confidence,
                "source_question": semantic_intent.source_question,
                "pending_filters": business_query.filters,
            },
        )

    def _find_missing_slots(
        self,
        query_type: BusinessQueryType,
        filters: dict,
        semantic_intent: BusinessSemanticIntent,
    ) -> list[ClarificationSlot]:
        intent_filters = semantic_intent.filters.model_dump(exclude_none=True)
        merged_filters = {**filters, **intent_filters}

        missing: list[ClarificationSlot] = []
        for slot in REQUIRED_SLOTS_BY_QUERY_TYPE[query_type]:
            filter_key = FILTER_KEY_BY_SLOT[slot]
            value = merged_filters.get(filter_key)
            if value is None or value == "":
                missing.append(slot)
        return missing
