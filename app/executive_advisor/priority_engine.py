from app.executive_advisor.constants import ADVISOR_MAX_ITEMS, PRIORITY_RANK
from app.executive_advisor.schemas import ExecutiveAgenda, ExecutiveAgendaItem


def prioritize_agenda(agenda: ExecutiveAgenda) -> ExecutiveAgenda:
    ranked = sorted(
        agenda.items,
        key=lambda item: (
            PRIORITY_RANK.get(item.priority, 99),
            -len(item.summary),
        ),
    )
    return ExecutiveAgenda(
        greeting=agenda.greeting,
        items=ranked[:ADVISOR_MAX_ITEMS],
    )


def boost_from_copilot(
    items: list[ExecutiveAgendaItem],
    proposals: list[dict],
) -> list[ExecutiveAgendaItem]:
    if not proposals:
        return items

    boosted: list[ExecutiveAgendaItem] = []
    seen_titles: set[str] = set()

    for proposal in proposals[:2]:
        title = str(proposal.get("title", "")).strip()
        query = str(proposal.get("query", "")).strip()
        rationale = str(proposal.get("rationale", "")).strip()
        if not title or not query or title in seen_titles:
            continue
        seen_titles.add(title)
        boosted.append(
            ExecutiveAgendaItem(
                title=title,
                summary=rationale or title,
                justification="Propuesta derivada del último análisis empresarial validado.",
                priority="Alta",
                expected_impact="Profundizar en el hallazgo más reciente.",
                suggested_query=query,
                action_label=str(proposal.get("action_label", "Analizar")),
            )
        )

    merged = boosted + [item for item in items if item.title not in seen_titles]
    return merged[:ADVISOR_MAX_ITEMS]
