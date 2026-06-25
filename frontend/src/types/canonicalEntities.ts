export interface EntityAlias {
  entity_id: number
  entity_code: string
  entity_name: string
  source_column: string
  resolution_rule: string
  resolution_score: string
}

export interface CanonicalEntityItem {
  canonical_id: number
  canonical_name: string
  normalized_name: string
  primary_rfc: string | null
  alias_count: number
  aliases: EntityAlias[]
  created_at: string
  updated_at: string
}

export interface CanonicalEntityListResponse {
  items: CanonicalEntityItem[]
  total: number
  page: number
  page_size: number
}

export interface SuggestionEntityRef {
  entity_id: number
  entity_code: string
  entity_name: string
  source_column: string
}

export interface CanonicalSuggestionItem {
  suggestion_id: number
  source_entity: SuggestionEntityRef
  candidate_entity: SuggestionEntityRef
  rule_used: string
  score: string
  status: string
  created_at: string
}

export interface CanonicalSuggestionListResponse {
  items: CanonicalSuggestionItem[]
  total: number
  page: number
  page_size: number
}

export interface CanonicalStatistics {
  canonical_entities_total: number
  canonical_matches: number
  pending_matches: number
  automatic_suggestions: number
  commercial_entities_total: number
  resolved_entities: number
  unresolved_entities: number
  unresolved_pct: number
  orphan_entities: number
  last_suggestion_run: string | null
}
