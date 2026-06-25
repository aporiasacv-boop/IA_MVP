import hashlib
import json
from datetime import datetime
from decimal import Decimal

from app.enterprise_knowledge.schemas import EnterpriseKnowledgeObjectSchema, KnowledgeItem
from app.enterprise_reasoning.schemas import EnterpriseReasoningObjectSchema, ReasoningConclusion
from app.evidence_package.constants import EEP_SCHEMA_ID, EEP_VERSION, SOURCE_EKO, SOURCE_ERO, SOURCE_SBEP
from app.evidence_package.schemas import (
    EnterpriseEvidencePackage,
    EvidenceConfidence,
    EvidenceItem,
    EvidenceLimitation,
)
from app.semantic_intent.schemas import BusinessExecutionPlan

EKO_SECTION_MAP = {
    "identity": lambda eko: eko.identity.items,
    "roles": lambda eko: eko.roles,
    "nature": lambda eko: eko.nature,
    "behaviors": lambda eko: eko.behaviors,
    "facts": lambda eko: eko.facts,
    "signals": lambda eko: eko.signals,
    "alerts": lambda eko: eko.alerts,
    "patterns": lambda eko: eko.patterns,
    "relationships": lambda eko: eko.relationships,
    "quality": lambda eko: eko.quality.items,
    "evidence": lambda eko: [],
}

ERO_SECTION_MAP = {
    "findings": lambda ero: ero.findings,
    "signals": lambda ero: ero.signals,
    "alerts": lambda ero: ero.alerts,
    "risks": lambda ero: ero.risks,
    "opportunities": lambda ero: ero.opportunities,
    "recommendations": lambda ero: ero.recommendations,
    "evidence": lambda ero: [],
}


def _knowledge_to_evidence(item: KnowledgeItem, section: str) -> EvidenceItem:
    return EvidenceItem(
        key=f"{section}:{item.key}",
        value=item.value,
        source=SOURCE_EKO,
        evidence={"section": section, **item.evidence},
        confidence=item.confidence,
        timestamp=item.computed_at,
    )


def _reasoning_to_evidence(item: ReasoningConclusion, section: str) -> EvidenceItem:
    return EvidenceItem(
        key=f"{section}:{item.key}",
        value=item.value,
        source=SOURCE_ERO,
        evidence={"section": section, "rule_code": item.rule_code, **item.evidence},
        confidence=item.confidence,
        timestamp=item.computed_at,
    )


def _avg_decimal(items: list[EvidenceItem]) -> Decimal | None:
    if not items:
        return None
    total = sum(float(i.confidence) for i in items)
    return Decimal(str(round(total / len(items), 4)))


def _build_limitations(
    *,
    plan: BusinessExecutionPlan,
    eko: EnterpriseKnowledgeObjectSchema | None,
    ero: EnterpriseReasoningObjectSchema | None,
    canonical_id: int | None,
) -> list[EvidenceLimitation]:
    limitations: list[EvidenceLimitation] = []
    if plan.incomplete:
        limitations.append(
            EvidenceLimitation(
                code="incomplete_plan",
                description="El plan de ejecución está incompleto",
                severity="high",
                source=SOURCE_SBEP,
            )
        )
    if plan.incompatible_strategy:
        limitations.append(
            EvidenceLimitation(
                code="incompatible_strategy",
                description="Estrategia de ejecución incompatible con el verbo detectado",
                severity="medium",
                source=SOURCE_SBEP,
            )
        )
    if canonical_id is None and plan.entity_hints:
        limitations.append(
            EvidenceLimitation(
                code="entity_unresolved",
                description="No se resolvió entidad canónica desde los hints",
                severity="high",
                source=SOURCE_SBEP,
            )
        )
    if eko is None and plan.required_knowledge:
        limitations.append(
            EvidenceLimitation(
                code="missing_eko",
                description="Enterprise Knowledge Object no disponible",
                severity="critical",
                source=SOURCE_EKO,
            )
        )
    if ero is None and plan.required_reasoning:
        limitations.append(
            EvidenceLimitation(
                code="missing_ero",
                description="Enterprise Reasoning Object no disponible",
                severity="high",
                source=SOURCE_ERO,
            )
        )
    if eko and not eko.evidence:
        limitations.append(
            EvidenceLimitation(
                code="eko_no_evidence_index",
                description="EKO sin índice de evidencia",
                severity="medium",
                source=SOURCE_EKO,
            )
        )
    return limitations


def build_evidence_package(
    *,
    question: str,
    plan: BusinessExecutionPlan,
    eko: EnterpriseKnowledgeObjectSchema | None,
    ero: EnterpriseReasoningObjectSchema | None,
    canonical_id: int | None,
    built_at: datetime | None = None,
) -> EnterpriseEvidencePackage:
    timestamp = built_at or datetime.now()

    knowledge_items: list[EvidenceItem] = []
    facts: list[EvidenceItem] = []
    signals: list[EvidenceItem] = []
    alerts: list[EvidenceItem] = []

    if eko:
        for section in plan.required_knowledge:
            if section == "evidence":
                continue
            getter = EKO_SECTION_MAP.get(section)
            if getter is None:
                continue
            for item in getter(eko):
                ev = _knowledge_to_evidence(item, section)
                knowledge_items.append(ev)
                if section == "facts":
                    facts.append(ev)
                elif section == "signals":
                    signals.append(ev)
                elif section == "alerts":
                    alerts.append(ev)

    reasoning_items: list[EvidenceItem] = []
    recommendations: list[EvidenceItem] = []

    if ero:
        for section in plan.required_reasoning:
            if section == "evidence":
                continue
            getter = ERO_SECTION_MAP.get(section)
            if getter is None:
                continue
            for item in getter(ero):
                ev = _reasoning_to_evidence(item, section)
                reasoning_items.append(ev)
                if section == "signals" and ev.key not in {s.key for s in signals}:
                    signals.append(ev)
                elif section == "alerts" and ev.key not in {a.key for a in alerts}:
                    alerts.append(ev)
                elif section == "recommendations":
                    recommendations.append(ev)

    evidence_index: list[dict] = []
    if eko:
        evidence_index.extend(
            {"source": SOURCE_EKO, **entry} for entry in (eko.evidence or [])
        )
    if ero:
        evidence_index.extend(
            {"source": SOURCE_ERO, **entry} for entry in (ero.evidence or [])
        )

    limitations = _build_limitations(
        plan=plan, eko=eko, ero=ero, canonical_id=canonical_id
    )

    all_items = knowledge_items + reasoning_items
    pkg_confidence = _avg_decimal(all_items) or plan.confidence
    if limitations:
        penalty = min(0.15 * len(limitations), 0.45)
        pkg_confidence = Decimal(str(round(max(float(pkg_confidence) - penalty, 0.0), 4)))

    package_id = hashlib.sha256(
        f"{question}|{plan.plan_id}|{canonical_id}|{timestamp.isoformat()}".encode()
    ).hexdigest()[:20]

    return EnterpriseEvidencePackage(
        schema_version=EEP_VERSION,
        package_id=package_id,
        question=question,
        execution_plan=plan,
        business_context={
            "detected_context": plan.detected_context,
            "detected_objects": plan.detected_objects,
            "detected_timeframe": plan.detected_timeframe,
            "entity_hints": plan.entity_hints,
            "constraints": plan.constraints,
            "canonical_id": canonical_id,
        },
        knowledge=knowledge_items,
        reasoning=reasoning_items,
        facts=facts,
        signals=signals,
        alerts=alerts,
        recommendations=recommendations,
        evidence=evidence_index,
        limitations=limitations,
        confidence=EvidenceConfidence(
            average_confidence=pkg_confidence,
            plan_confidence=plan.confidence,
            knowledge_confidence=_avg_decimal(knowledge_items),
            reasoning_confidence=_avg_decimal(reasoning_items),
            items_count=len(all_items),
        ),
        metadata={
            "schema_id": EEP_SCHEMA_ID,
            "built_at": timestamp.isoformat(),
            "execution_strategy": plan.execution_strategy,
            "deterministic": True,
            "contains_sql": False,
            "contains_llm_output": False,
            "canonical_id": canonical_id,
        },
    )


def package_size_bytes(package: EnterpriseEvidencePackage) -> int:
    return len(json.dumps(package.model_dump(mode="json"), ensure_ascii=False).encode("utf-8"))


def count_evidence_items(package: EnterpriseEvidencePackage) -> int:
    return (
        len(package.knowledge)
        + len(package.reasoning)
        + len(package.evidence)
    )
