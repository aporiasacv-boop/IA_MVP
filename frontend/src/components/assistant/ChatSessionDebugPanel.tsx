import { DEBUG_MODE } from '../../config/featureFlags'
import { es } from '../../i18n/spanish'
import { chatSessionManager } from '../../services/chatSessionManager'

interface ChatSessionDebugPanelProps {
  sessionId: string | null
  isClarificationPending: boolean
  clarificationCompletionRate: number
  lastClarificationResolved?: boolean
}

export function ChatSessionDebugPanel({
  sessionId,
  isClarificationPending,
  clarificationCompletionRate,
  lastClarificationResolved,
}: ChatSessionDebugPanelProps) {
  if (!DEBUG_MODE) return null

  const metrics = chatSessionManager.getMetrics()

  return (
    <div className="mb-4 rounded-xl border border-dashed border-amber-300/80 bg-amber-50/60 px-4 py-3 text-[11px] text-amber-950">
      <p className="font-semibold uppercase tracking-[0.14em]">Depuración — sesión conversacional</p>
      <dl className="mt-2 grid gap-1 sm:grid-cols-2">
        <div>
          <dt className="text-amber-800/80">{es.chat.sessionId}</dt>
          <dd className="font-mono text-[10px] break-all">{sessionId ?? '—'}</dd>
        </div>
        <div>
          <dt className="text-amber-800/80">{es.chat.pendingClarification}</dt>
          <dd>{isClarificationPending ? 'Sí' : 'No'}</dd>
        </div>
        <div>
          <dt className="text-amber-800/80">{es.chat.clarificationResolved} (última)</dt>
          <dd>
            {lastClarificationResolved === undefined
              ? '—'
              : lastClarificationResolved
                ? 'Sí'
                : 'No'}
          </dd>
        </div>
        <div>
          <dt className="text-amber-800/80">Tasa de aclaraciones completadas</dt>
          <dd>{(clarificationCompletionRate * 100).toFixed(0)}%</dd>
        </div>
        <div>
          <dt className="text-amber-800/80">Sesiones iniciadas</dt>
          <dd>{metrics.conversation_sessions_started}</dd>
        </div>
        <div>
          <dt className="text-amber-800/80">Sesiones reutilizadas</dt>
          <dd>{metrics.conversation_sessions_reused}</dd>
        </div>
      </dl>
    </div>
  )
}
