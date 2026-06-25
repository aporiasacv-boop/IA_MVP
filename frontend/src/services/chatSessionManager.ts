import type { HybridChatResult } from '../types/hybrid-chat'

const SESSION_ID_KEY = 'ia_mvp_chat_session_id'
const PENDING_CLARIFICATION_KEY = 'ia_mvp_chat_pending_clarification'
const METRICS_KEY = 'ia_mvp_chat_session_metrics'

export interface ChatSessionMetrics {
  conversation_sessions_started: number
  conversation_sessions_reused: number
  clarifications_started: number
  clarifications_completed: number
}

const DEFAULT_METRICS: ChatSessionMetrics = {
  conversation_sessions_started: 0,
  conversation_sessions_reused: 0,
  clarifications_started: 0,
  clarifications_completed: 0,
}

function readMetrics(): ChatSessionMetrics {
  try {
    const raw = sessionStorage.getItem(METRICS_KEY)
    if (!raw) return { ...DEFAULT_METRICS }
    return { ...DEFAULT_METRICS, ...(JSON.parse(raw) as Partial<ChatSessionMetrics>) }
  } catch {
    return { ...DEFAULT_METRICS }
  }
}

function writeMetrics(metrics: ChatSessionMetrics): void {
  sessionStorage.setItem(METRICS_KEY, JSON.stringify(metrics))
}

export function generateSessionId(): string {
  return crypto.randomUUID().replace(/-/g, '')
}

function readSessionId(): string | null {
  const value = sessionStorage.getItem(SESSION_ID_KEY)
  return value && value.length > 0 ? value : null
}

function writeSessionId(sessionId: string): void {
  sessionStorage.setItem(SESSION_ID_KEY, sessionId)
}

/** Gestiona session_id y estado de aclaración en sessionStorage (por pestaña). */
export const chatSessionManager = {
  getSessionId(): string | null {
    return readSessionId()
  },

  /** Obtiene session_id existente o crea uno nuevo. */
  ensureSessionId(): { sessionId: string; isNew: boolean } {
    const existing = readSessionId()
    if (existing) {
      return { sessionId: existing, isNew: false }
    }
    const sessionId = generateSessionId()
    writeSessionId(sessionId)
    return { sessionId, isNew: true }
  },

  /** Backend es fuente de verdad para el identificador de sesión. */
  setSessionIdFromBackend(sessionId: string): void {
    if (!sessionId) return
    writeSessionId(sessionId)
  },

  isPendingClarification(): boolean {
    return sessionStorage.getItem(PENDING_CLARIFICATION_KEY) === 'true'
  },

  setPendingClarification(pending: boolean): void {
    if (pending) {
      sessionStorage.setItem(PENDING_CLARIFICATION_KEY, 'true')
    } else {
      sessionStorage.removeItem(PENDING_CLARIFICATION_KEY)
    }
  },

  startNewConversation(): string {
    const sessionId = generateSessionId()
    writeSessionId(sessionId)
    sessionStorage.removeItem(PENDING_CLARIFICATION_KEY)
    const metrics = readMetrics()
    metrics.conversation_sessions_started += 1
    writeMetrics(metrics)
    return sessionId
  },

  recordSessionStarted(): void {
    const metrics = readMetrics()
    metrics.conversation_sessions_started += 1
    writeMetrics(metrics)
  },

  recordSessionReused(): void {
    const metrics = readMetrics()
    metrics.conversation_sessions_reused += 1
    writeMetrics(metrics)
  },

  recordClarificationStarted(): void {
    const metrics = readMetrics()
    metrics.clarifications_started += 1
    writeMetrics(metrics)
  },

  recordClarificationCompleted(): void {
    const metrics = readMetrics()
    metrics.clarifications_completed += 1
    writeMetrics(metrics)
  },

  getMetrics(): ChatSessionMetrics {
    return readMetrics()
  },

  getClarificationCompletionRate(): number {
    const { clarifications_started, clarifications_completed } = readMetrics()
    if (clarifications_started === 0) return 0
    return clarifications_completed / clarifications_started
  },

  wasClarificationResolved(metadata: Record<string, unknown>): boolean {
    return metadata.clarification_resolved === true
  },

  /** Sincroniza sesión y estado de aclaración desde la respuesta hybrid. */
  syncFromHybridResponse(result: HybridChatResult): void {
    const metadata = result.metadata ?? {}

    if (typeof metadata.session_id === 'string') {
      this.setSessionIdFromBackend(metadata.session_id)
    }

    if (result.handled_by === 'slot_clarification') {
      this.setPendingClarification(true)
      this.recordClarificationStarted()
      return
    }

    if (this.wasClarificationResolved(metadata)) {
      this.setPendingClarification(false)
      this.recordClarificationCompleted()
      return
    }

    if (this.isPendingClarification() && result.handled_by !== 'slot_clarification') {
      this.setPendingClarification(false)
    }
  },

  /** Reinicia almacenamiento (tests). */
  resetForTests(): void {
    sessionStorage.removeItem(SESSION_ID_KEY)
    sessionStorage.removeItem(PENDING_CLARIFICATION_KEY)
    sessionStorage.removeItem(METRICS_KEY)
  },
}

/** Oculta sugerencias y UI de descubrimiento mientras hay aclaración pendiente. */
export function shouldSuppressFollowUpUi(
  result: HybridChatResult,
  pendingClarification: boolean,
): boolean {
  if (pendingClarification) return true
  if (result.handled_by === 'slot_clarification') return true
  if (result.handled_by === 'capability_discovery') return true
  if (result.handled_by === 'guided_fallback') return true
  return false
}
