export interface KnowledgeItem {
  key: string
  value: unknown
  source: string
  evidence: Record<string, unknown>
  confidence: string
  computed_at: string
}

export interface KnowledgeIdentity {
  canonical_id: number
  canonical_name: string
  normalized_name: string
  primary_rfc?: string | null
  alias_count: number
  aliases: Array<Record<string, unknown>>
  items: KnowledgeItem[]
}

export interface KnowledgeQuality {
  completeness: string
  average_confidence: string
  profile_completeness?: string | null
  has_profile: boolean
  has_ontology: boolean
  ontology_assignment_count: number
  items: KnowledgeItem[]
}

export interface EnterpriseKnowledgeObject {
  schema_version: string
  canonical_id: number
  identity: KnowledgeIdentity
  roles: KnowledgeItem[]
  nature: KnowledgeItem[]
  behaviors: KnowledgeItem[]
  facts: KnowledgeItem[]
  signals: KnowledgeItem[]
  alerts: KnowledgeItem[]
  patterns: KnowledgeItem[]
  relationships: KnowledgeItem[]
  quality: KnowledgeQuality
  evidence: Array<Record<string, unknown>>
  metadata: Record<string, unknown>
}

export interface KnowledgeListItem {
  knowledge_id: number
  canonical_id: number
  canonical_name: string
  completeness: string
  average_confidence: string
  built_at: string
}

export interface KnowledgeListResponse {
  items: KnowledgeListItem[]
  total: number
  page: number
  page_size: number
}

export interface KnowledgeStatistics {
  knowledge_objects_total: number
  canonical_entities_total: number
  knowledge_build_time: number
  knowledge_average_completeness: number
  knowledge_average_confidence: number
  knowledge_last_refresh?: string | null
  incomplete_objects: number
}

export interface KnowledgeSchema {
  schema_id: string
  schema_version: string
  required_sections: string[]
  knowledge_item_fields: string[]
  description: string
}
