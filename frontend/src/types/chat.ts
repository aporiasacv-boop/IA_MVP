export type ResponseMode = 'DETERMINISTIC' | 'GENERATIVE'

export interface ExtractedEntities {
  month?: number | null
  year?: number | null
  client_code?: string | null
  account_code?: string | null
  period?: string | null
}

export interface ChatTimings {
  spell_correction_ms: number
  synonym_resolution_ms: number
  intent_normalization_ms: number
  social_layer_ms?: number
  identity_layer_ms?: number
  token_optimization_ms?: number
  system_explanation_ms?: number
  capability_layer_ms?: number
  entity_extraction_ms: number
  router_ms: number
  deterministic_ms: number
  query_ms: number
  context_ms: number
  prompt_ms: number
  llm_ms: number
  total_ms: number
}

export interface PromptMetrics {
  prompt_chars: number
  context_chars: number
  question_chars: number
  response_chars: number
  estimated_tokens: number
  sources_used: string[]
}

export interface ChatApiResponse {
  intent: string
  intent_confidence: number
  response_mode: ResponseMode
  answer: string
  data: unknown
  original_question: string
  normalized_question: string
  corrections_applied: string[]
  entities: ExtractedEntities
  sources: string[]
  timings: ChatTimings
  prompt_metrics: PromptMetrics
}

export interface BusinessCopilotProposal {
  title: string
  rationale: string
  actionLabel: string
  query: string
  proposalType: string
}

export interface ExecutiveInsight {
  executiveSummary?: string
  businessInterpretation?: string
  findings?: string[]
  possibleRisks: string[]
  opportunities?: string[]
  recommendations: string[]
  limitations?: string[]
  nextAnalyses?: string[]
}

export interface HybridMessageMeta {
  handledBy: string
  queryType?: string
  confidence?: number
  success: boolean
  rawMetadata: Record<string, unknown>
  sessionId?: string
  pendingClarification?: boolean
  clarificationResolved?: boolean
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  intent?: string
  intentConfidence?: number
  responseMode?: ResponseMode
  timings?: ChatTimings
  promptMetrics?: PromptMetrics
  sources?: string[]
  hybrid?: HybridMessageMeta
  suggestedQuestions?: string[]
  isError?: boolean
  timestamp: Date
}

export interface RecentQuery {
  id: string
  question: string
  askedAt: Date
}

export class ChatApiError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'ChatApiError'
  }
}
