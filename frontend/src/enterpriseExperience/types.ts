export type ExperienceScreen = 'enterprise_ai' | 'executive_dashboard' | 'financial_simulator'

export type AiActionIntent = 'analyze' | 'explain'

export interface EnterpriseExperienceContext {
  period: string | null
  scenario: string | null
  company: string | null
  lastQuery: string | null
  lastScreen: ExperienceScreen | null
}

export interface PinnedQuery {
  id: string
  question: string
  pinnedAt: string
}

export interface StoredRecentQuery {
  id: string
  question: string
  askedAt: string
}

export interface SerializedChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  isError?: boolean
  timestamp: string
}

export interface NavigationTelemetry {
  navigation_origin: string
  navigation_target: string
  deep_link_used: boolean
  context_restored: boolean
  recorded_at: string
}

export interface EnterpriseExperienceSnapshot {
  context: EnterpriseExperienceContext
  pinnedQueries: PinnedQuery[]
  recentQueries: StoredRecentQuery[]
  conversation: SerializedChatMessage[]
  lastNavigation: NavigationTelemetry | null
}

export const DEFAULT_CONTEXT: EnterpriseExperienceContext = {
  period: null,
  scenario: null,
  company: null,
  lastQuery: null,
  lastScreen: null,
}
