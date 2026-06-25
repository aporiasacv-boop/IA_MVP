from app.guided_fallback.v2.domains import (
    DOMAIN_DISPLAY_LABELS,
    SUPPORTED_CAPABILITIES,
    BusinessDomain,
)


def build_domain_contextual_answer(domain: BusinessDomain) -> str:
    label = DOMAIN_DISPLAY_LABELS[domain]
    lines = [
        f"Detecté una consulta relacionada con {label}.",
        "",
        f"Actualmente no dispongo de información de {label}.",
        "",
        "Puedo ayudarte con información sobre:",
        "",
    ]
    lines.extend(f"• {capability}" for capability in SUPPORTED_CAPABILITIES)
    return "\n".join(lines)
