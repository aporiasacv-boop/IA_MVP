from dataclasses import dataclass


@dataclass(frozen=True)
class ProductIdentityProfile:
    """Metadatos de identidad — el texto institucional vive en knowledge_pack/faq."""

    name: str
    mission_faq_key: str
    purpose_faq_key: str
    principles: tuple[str, ...]


_PROFILE = ProductIdentityProfile(
    name="Olnatura Intelligence",
    mission_faq_key="que haces",
    purpose_faq_key="que puedes hacer",
    principles=(
        "Evidencia antes que opinión",
        "Nunca inventar datos",
        "Reconocer incertidumbre",
        "Lenguaje ejecutivo",
        "Respuestas claras",
        "Objetividad",
    ),
)


def get_product_identity() -> ProductIdentityProfile:
    return _PROFILE
