EKO_VERSION = "1.0.0"
EKO_SCHEMA_ID = "enterprise_knowledge_object_v1"

SOURCE_MASTER = "business_entity_master"
SOURCE_CANONICAL = "canonical_business_entity"
SOURCE_PROFILE = "business_entity_profile"
SOURCE_ONTOLOGY = "business_ontology"

REQUIRED_SECTIONS = frozenset({
    "identity",
    "roles",
    "nature",
    "behaviors",
    "facts",
    "signals",
    "alerts",
    "patterns",
    "relationships",
    "quality",
    "evidence",
    "metadata",
})

SORTABLE_KNOWLEDGE_FIELDS = frozenset({
    "completeness",
    "average_confidence",
    "built_at",
    "canonical_name",
})
