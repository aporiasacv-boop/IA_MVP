export interface OntologyTypeItem {
  type_id: number
  concept_category: string
  type_code: string
  type_label: string
  description?: string | null
  is_active: boolean
  sort_order: number
}

export interface OntologyAssignmentItem {
  assignment_id: number
  canonical_id: number
  concept_category: string
  type_code: string
  type_label: string
  rule_code: string
  evidence_json: Record<string, unknown>
  score: number
  confidence: number
  status: string
  created_at: string
}

export interface IdentitySummary {
  canonical_id: number
  canonical_name: string
  primary_rfc?: string | null
  normalized_name: string
  alias_count: number
}

export interface ProfileSummary {
  total_movements: number
  total_amount: number
  debit_credit_ratio?: number | null
  dimensions_used: string[]
  profile_completeness: number
}

export interface OntologyEntityView {
  identity: IdentitySummary
  profile_summary?: ProfileSummary | null
  assignments: OntologyAssignmentItem[]
  top_suggestions: OntologyAssignmentItem[]
}

export interface OntologyListResponse {
  items: OntologyEntityView[]
  total: number
  page: number
  page_size: number
}

export interface OntologyStatistics {
  ontology_entities: number
  ontology_pending: number
  ontology_approved: number
  ontology_rejected: number
  ontology_rules: number
  ontology_types: number
  ontology_average_confidence: number
  entities_without_suggestions: number
  last_ontology_run?: string | null
}
