export interface BusinessVerbDefinition {
  verb_id: string
  category: string
  aliases: string[]
  enabled: boolean
}

export interface VerbCatalogResponse {
  version: string
  verbs: BusinessVerbDefinition[]
  total: number
  enabled_count: number
}

export interface DetectedVerb {
  verb_id: string
  category: string
  matched_text: string
  confidence: string
}

export interface DetectedObject {
  object_id: string
  matched_text: string
  confidence: string
  ambiguous: boolean
}

export interface SemanticParseResult {
  schema_version: string
  original_question: string
  normalized_question: string
  business_verb?: DetectedVerb | null
  business_objects: DetectedObject[]
  business_context: string[]
  business_scope: string[]
  business_time: string[]
  business_constraints: string[]
  entity_hints: string[]
  unknown_tokens: string[]
  confidence: string
  parsed_at: string
  metadata: Record<string, unknown>
}

export interface BusinessExecutionPlan {
  schema_version: string
  plan_id: string
  original_question: string
  detected_verb?: string | null
  detected_objects: string[]
  detected_context: string[]
  detected_timeframe: string[]
  required_knowledge: string[]
  required_reasoning: string[]
  required_evidence: string[]
  execution_strategy: string
  confidence: string
  entity_hints: string[]
  constraints: string[]
  incomplete: boolean
  incompatible_strategy: boolean
  planned_at: string
  metadata: Record<string, unknown>
}

export interface SemanticStatistics {
  semantic_parses: number
  execution_plans: number
  verb_distribution: Record<string, number>
  average_semantic_confidence: number
  planner_success_rate: number
  unknown_verbs: number
}
