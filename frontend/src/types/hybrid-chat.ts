export interface SuggestedQuestionsResult {
  questions: string[]
  source: string
  confidence: number
  metadata: Record<string, unknown>
}

export interface HybridChatResult {
  handled_by: string
  success: boolean
  answer: string
  suggestions?: SuggestedQuestionsResult | null
  metadata: Record<string, unknown>
}
