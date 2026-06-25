EEP_VERSION = "1.0.0"
EEP_SCHEMA_ID = "enterprise_evidence_package_v1"

SOURCE_SBEP = "semantic_business_execution_planner"
SOURCE_EKO = "enterprise_knowledge_object"
SOURCE_ERO = "enterprise_reasoning_object"

EXAMPLE_QUESTION = "Evaluar riesgos del cliente con mayor volumen este mes"

REQUIRED_SECTIONS = (
    "question",
    "execution_plan",
    "business_context",
    "knowledge",
    "reasoning",
    "facts",
    "signals",
    "alerts",
    "recommendations",
    "evidence",
    "limitations",
    "confidence",
    "metadata",
)
