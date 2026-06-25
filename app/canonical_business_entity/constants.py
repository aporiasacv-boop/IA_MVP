SOURCE_COLUMN_VENDOR = "cuenta_proveedor"
SOURCE_COLUMN_CUSTOMER = "cuenta_cliente"

COMMERCIAL_SOURCE_COLUMNS = frozenset({SOURCE_COLUMN_VENDOR, SOURCE_COLUMN_CUSTOMER})

SUGGESTION_PENDING = "pending"
SUGGESTION_ACCEPTED = "accepted"
SUGGESTION_REJECTED = "rejected"

RULE_SINGLETON_BOOTSTRAP = "singleton_bootstrap"
RULE_RFC_EXACT = "rfc_exact"
RULE_NORMALIZED_NAME_EXACT = "normalized_name_exact"
RULE_TOKEN_OVERLAP = "token_overlap"
RULE_FUZZY_NAME = "fuzzy_name_similarity"
RULE_BRAND_TOKEN = "brand_token_match"

MIN_SUGGESTION_SCORE = 0.55
MIN_TOKEN_OVERLAP_SCORE = 0.70
MIN_FUZZY_SCORE = 0.82

SORTABLE_CANONICAL_FIELDS = frozenset({
    "canonical_name",
    "normalized_name",
    "alias_count",
    "updated_at",
})
