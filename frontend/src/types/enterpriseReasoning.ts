export interface ReasoningConclusion {
  key: string
  value: unknown
  rule_code: string
  evidence: Record<string, unknown>
  confidence: string
  severity: string
  computed_at: string
}

export interface ReasoningConfidence {
  average_confidence: string
  conclusions_count: number
  rules_executed: number
  items: ReasoningConclusion[]
}

export interface EnterpriseReasoningObject {
  schema_version: string
  canonical_id: number
  findings: ReasoningConclusion[]
  signals: ReasoningConclusion[]
  alerts: ReasoningConclusion[]
  risks: ReasoningConclusion[]
  opportunities: ReasoningConclusion[]
  recommendations: ReasoningConclusion[]
  evidence: Array<Record<string, unknown>>
  confidence: ReasoningConfidence
  metadata: Record<string, unknown>
}

export interface ReasoningListItem {
  reasoning_id: number
  canonical_id: number
  canonical_name: string
  average_confidence: string
  findings_count: number
  alerts_count: number
  recommendations_count: number
  built_at: string
}

export interface ReasoningListResponse {
  items: ReasoningListItem[]
  total: number
  page: number
  page_size: number
}

export interface ReasoningStatistics {
  reasoning_objects_total: number
  knowledge_objects_total: number
  reasoning_rules_executed: number
  average_reasoning_confidence: number
  average_findings: number
  average_alerts: number
  average_recommendations: number
  last_reasoning_refresh?: string | null
  incomplete_objects: number
}

export interface ReasoningRuleDefinition {
  rule_code: string
  conclusion_type: string
  key: string
  severity: string
  confidence: string
  enabled: boolean
  pack_id: string
  description: string
}

export interface ReasoningRulesResponse {
  packs: Array<{
    pack_id: string
    version: string
    rules: ReasoningRuleDefinition[]
  }>
  total_rules: number
  enabled_rules: number
}
