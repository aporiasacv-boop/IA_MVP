import type {
  EnterpriseExperienceContext,
  EnterpriseExperienceSnapshot,
  NavigationTelemetry,
  PinnedQuery,
  SerializedChatMessage,
  StoredRecentQuery,
} from './types'

const STORAGE_KEY = 'ia_mvp_enterprise_experience_v1'

function emptySnapshot(): EnterpriseExperienceSnapshot {
  return {
    context: {
      period: null,
      scenario: null,
      company: null,
      lastQuery: null,
      lastScreen: null,
    },
    pinnedQueries: [],
    recentQueries: [],
    conversation: [],
    lastNavigation: null,
  }
}

function readSnapshot(): EnterpriseExperienceSnapshot {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (!raw) return emptySnapshot()
    const parsed = JSON.parse(raw) as Partial<EnterpriseExperienceSnapshot>
    return {
      ...emptySnapshot(),
      ...parsed,
      context: { ...emptySnapshot().context, ...parsed.context },
      pinnedQueries: parsed.pinnedQueries ?? [],
      recentQueries: parsed.recentQueries ?? [],
      conversation: parsed.conversation ?? [],
    }
  } catch {
    return emptySnapshot()
  }
}

function writeSnapshot(snapshot: EnterpriseExperienceSnapshot): void {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot))
}

let snapshot = readSnapshot()
const listeners = new Set<() => void>()

function notify(): void {
  listeners.forEach((listener) => listener())
}

function update(mutator: (current: EnterpriseExperienceSnapshot) => EnterpriseExperienceSnapshot): void {
  snapshot = mutator(snapshot)
  writeSnapshot(snapshot)
  notify()
}

export const enterpriseExperienceStore = {
  subscribe(listener: () => void): () => void {
    listeners.add(listener)
    return () => listeners.delete(listener)
  },

  getSnapshot(): EnterpriseExperienceSnapshot {
    return snapshot
  },

  getContext(): EnterpriseExperienceContext {
    return snapshot.context
  },

  getLastNavigation(): NavigationTelemetry | null {
    return snapshot.lastNavigation
  },

  setContext(partial: Partial<EnterpriseExperienceContext>): void {
    update((current) => ({
      ...current,
      context: { ...current.context, ...partial },
    }))
  },

  recordNavigation(event: Omit<NavigationTelemetry, 'recorded_at'>): void {
    update((current) => ({
      ...current,
      lastNavigation: { ...event, recorded_at: new Date().toISOString() },
    }))
  },

  setConversation(messages: SerializedChatMessage[]): void {
    update((current) => ({
      ...current,
      conversation: messages.slice(-40),
    }))
  },

  addRecentQuery(question: string): void {
    const trimmed = question.trim()
    if (!trimmed) return
    update((current) => {
      const entry: StoredRecentQuery = {
        id: crypto.randomUUID(),
        question: trimmed,
        askedAt: new Date().toISOString(),
      }
      const filtered = current.recentQueries.filter((q) => q.question !== trimmed)
      return {
        ...current,
        recentQueries: [entry, ...filtered].slice(0, 12),
        context: { ...current.context, lastQuery: trimmed },
      }
    })
  },

  togglePin(question: string): void {
    const trimmed = question.trim()
    if (!trimmed) return
    update((current) => {
      const exists = current.pinnedQueries.some((q) => q.question === trimmed)
      if (exists) {
        return {
          ...current,
          pinnedQueries: current.pinnedQueries.filter((q) => q.question !== trimmed),
        }
      }
      const entry: PinnedQuery = {
        id: crypto.randomUUID(),
        question: trimmed,
        pinnedAt: new Date().toISOString(),
      }
      return {
        ...current,
        pinnedQueries: [entry, ...current.pinnedQueries].slice(0, 8),
      }
    })
  },

  isPinned(question: string): boolean {
    return snapshot.pinnedQueries.some((q) => q.question === question)
  },

  resetConversation(): void {
    update((current) => ({ ...current, conversation: [] }))
  },

  /** Solo para pruebas. */
  _resetForTests(): void {
    snapshot = emptySnapshot()
    sessionStorage.removeItem(STORAGE_KEY)
    notify()
  },
}

export function pathToScreen(pathname: string): string {
  if (pathname === '/' || pathname === '') return 'enterprise_ai'
  if (pathname.startsWith('/dashboard')) return 'executive_dashboard'
  if (pathname.startsWith('/financiero')) return 'financial_simulator'
  return pathname
}
