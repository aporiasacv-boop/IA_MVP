EXECUTIVE_RESPONSE_SCHEMA_ID = "executive_response_v1"
EXECUTIVE_RESPONSE_VERSION = "1.0.0"

EXECUTIVE_VERBS = frozenset({
    "evaluar",
    "diagnosticar",
    "justificar",
    "recomendar",
    "priorizar",
    "interpretar",
})

PROVIDER_OPENAI = "openai"
PROVIDER_CLAUDE = "claude"
PROVIDER_OLLAMA = "ollama"
PROVIDER_MOCK = "mock"

SUPPORTED_PROVIDERS = frozenset({
    PROVIDER_OPENAI,
    PROVIDER_CLAUDE,
    PROVIDER_OLLAMA,
    PROVIDER_MOCK,
})

MIN_EVIDENCE_ITEMS = 1
MIN_CONFIDENCE_THRESHOLD = 0.0
