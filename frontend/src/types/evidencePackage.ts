import type { BusinessExecutionPlan } from './semanticIntent'

export interface EvidenceItem {
  key: string
  value: unknown
  source: string
  evidence: Record<string, unknown>
  confidence: string
  timestamp: string
}

export interface EvidenceLimitation {
  code: string
  description: string
  severity: string
  source: string
}

export interface EvidenceConfidence {
  average_confidence: string
  plan_confidence: string
  knowledge_confidence?: string | null
  reasoning_confidence?: string | null
  items_count: number
}

export interface EnterpriseEvidencePackage {
  schema_version: string
  package_id: string
  question: string
  execution_plan: BusinessExecutionPlan
  business_context: Record<string, unknown>
  knowledge: EvidenceItem[]
  reasoning: EvidenceItem[]
  facts: EvidenceItem[]
  signals: EvidenceItem[]
  alerts: EvidenceItem[]
  recommendations: EvidenceItem[]
  evidence: Array<Record<string, unknown>>
  limitations: EvidenceLimitation[]
  confidence: EvidenceConfidence
  metadata: Record<string, unknown>
}

export interface EvidenceStatistics {
  evidence_packages_total: number
  average_package_size: number
  average_evidence_items: number
  average_confidence: number
  missing_evidence: number
  package_build_time: number
}

export interface EvidenceSchema {
  schema_id: string
  schema_version: string
  required_sections: string[]
  evidence_item_fields: string[]
  description: string
}
