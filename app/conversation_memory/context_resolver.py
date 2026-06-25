from dataclasses import dataclass
import re
from typing import Literal

from app.conversation_memory.schemas import ConversationContext
from app.conversation_memory.slot_value_parser import parse_slot_value
from app.domain.entities import BusinessEntity
from app.domain.operations import BusinessOperation
from app.query_engine.business_query import BusinessQuery
from app.query_engine.query_types import BusinessQueryType
from app.slot_clarification.required_slots import FILTER_KEY_BY_SLOT
from app.slot_clarification.slots import ClarificationSlot
from app.utils.text_normalizer import normalize_for_matching, normalize_text

ResolutionType = Literal["clarification", "follow_up"]

NEW_QUESTION_SIGNALS: tuple[str, ...] = (
    "cuantos",
    "cuántos",
    "cual",
    "cuál",
    "que ",
    "qué ",
    "como",
    "cómo",
    "muestrame",
    "muéstrame",
    "existen",
    "tienes",
    "puedo preguntarte",
)

COUNT_ENTITY_FOLLOW_UPS: dict[str, BusinessQueryType] = {
    "clientes": BusinessQueryType.COUNT_CLIENTES,
    "cliente": BusinessQueryType.COUNT_CLIENTES,
    "proveedores": BusinessQueryType.COUNT_PROVEEDORES,
    "proveedor": BusinessQueryType.COUNT_PROVEEDORES,
}

MONTH_TO_INT: dict[str, int] = {
    normalize_text(name): index
    for index, name in enumerate(
        (
            "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
        ),
        start=1,
    )
}


@dataclass(frozen=True)
class ContextResolution:
    query: BusinessQuery
    resolution_type: ResolutionType
    inherited_from: str


class ContextResolver:
    """Resuelve clarificaciones pendientes y follow-ups cortos de forma conservadora."""

    def resolve(
        self,
        message: str,
        context: ConversationContext | None,
    ) -> ContextResolution | None:
        if context is None:
            return None

        if context.pending_clarification and is_new_question(message):
            return None

        if context.pending_clarification:
            clarification = self._resolve_pending_clarification(message, context)
            if clarification is not None:
                return clarification

        if is_follow_up(message):
            follow_up = self._resolve_follow_up(message, context)
            if follow_up is not None:
                return follow_up

        return None

    def _resolve_pending_clarification(
        self,
        message: str,
        context: ConversationContext,
    ) -> ContextResolution | None:
        pending = context.pending_clarification
        if not pending:
            return None

        missing_slots: list[str] = pending.get("missing_slots", [])
        if not missing_slots:
            return None

        primary_slot = missing_slots[0]
        parsed_value = parse_slot_value(message, primary_slot)
        if parsed_value is None:
            return None

        filter_key = FILTER_KEY_BY_SLOT[ClarificationSlot(primary_slot)]
        merged_filters = {
            **pending.get("pending_filters", {}),
            **context.last_filters,
            filter_key: parsed_value,
        }

        query_type = BusinessQueryType(pending["pending_query_type"])
        return ContextResolution(
            query=BusinessQuery(query_type=query_type, filters=merged_filters),
            resolution_type="clarification",
            inherited_from=context.last_query_type or query_type.value,
        )

    def _resolve_follow_up(
        self,
        message: str,
        context: ConversationContext,
    ) -> ContextResolution | None:
        if not context.last_query_type:
            return None

        remainder = _follow_up_remainder(message)
        if not remainder:
            return None

        last_type = BusinessQueryType(context.last_query_type)

        count_follow_up = self._resolve_count_entity_follow_up(remainder, last_type)
        if count_follow_up is not None:
            return ContextResolution(
                query=count_follow_up,
                resolution_type="follow_up",
                inherited_from=last_type.value,
            )

        month_follow_up = self._resolve_month_follow_up(remainder, context, last_type)
        if month_follow_up is not None:
            return ContextResolution(
                query=month_follow_up,
                resolution_type="follow_up",
                inherited_from=last_type.value,
            )

        return None

    @staticmethod
    def _resolve_count_entity_follow_up(
        remainder: str,
        last_type: BusinessQueryType,
    ) -> BusinessQuery | None:
        if last_type not in {
            BusinessQueryType.COUNT_CLIENTES,
            BusinessQueryType.COUNT_PROVEEDORES,
        }:
            return None

        target_type = COUNT_ENTITY_FOLLOW_UPS.get(remainder)
        if target_type is None or target_type == last_type:
            return None

        return BusinessQuery(query_type=target_type, filters={})

    @staticmethod
    def _resolve_month_follow_up(
        remainder: str,
        context: ConversationContext,
        last_type: BusinessQueryType,
    ) -> BusinessQuery | None:
        if last_type != BusinessQueryType.MAX_PROVEEDOR_MES:
            return None

        if context.last_operation != BusinessOperation.MAX.value:
            return None
        if context.last_target_entity != BusinessEntity.PROVEEDOR.value:
            return None

        month_text = remainder.removeprefix("en ").strip()
        mes = MONTH_TO_INT.get(month_text)
        if mes is None and _MONTH_INT_PATTERN.match(month_text):
            mes = int(month_text)

        if mes is None:
            return None

        filters = {**context.last_filters, "mes": mes}
        return BusinessQuery(query_type=BusinessQueryType.MAX_PROVEEDOR_MES, filters=filters)


_MONTH_INT_PATTERN = re.compile(r"^(1[0-2]|[1-9])$")


def is_follow_up(message: str) -> bool:
    normalized = normalize_for_matching(message)
    return normalized.startswith("y ")


def is_new_question(message: str) -> bool:
    normalized = normalize_for_matching(message)
    if is_follow_up(message):
        return False
    if len(normalized) <= 12 and not any(ch in normalized for ch in ("?", "¿")):
        return False
    return any(signal in normalized for signal in NEW_QUESTION_SIGNALS)


def _follow_up_remainder(message: str) -> str:
    normalized = normalize_for_matching(message)
    if not normalized.startswith("y "):
        return ""
    return normalized[2:].strip()
