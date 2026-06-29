import { es, translateReasoningRoute } from '../../i18n/spanish'
import type { ChatMessage } from '../../types/chat'

interface EnterpriseReasoningDebugProps {
  message: ChatMessage
}

function formatConfidence(value: unknown): string {
  if (typeof value !== 'number') return '—'
  return `${(value * 100).toFixed(0)}%`
}

function formatMatch(value: unknown): string {
  if (value === true) return 'Sí'
  if (value === false) return 'No'
  return '—'
}

export function EnterpriseReasoningDebug({ message }: EnterpriseReasoningDebugProps) {
  const metadata = message.hybrid?.rawMetadata
  if (!metadata?.reasoning_intent) return null

  const rows = [
    { label: es.reasoning.intent, value: String(metadata.reasoning_intent) },
    { label: es.reasoning.confidence, value: formatConfidence(metadata.reasoning_confidence) },
    {
      label: es.reasoning.recommendedRoute,
      value: translateReasoningRoute(metadata.reasoning_route),
    },
    {
      label: es.reasoning.actualRoute,
      value: translateReasoningRoute(metadata.reasoning_actual_route),
    },
    { label: es.reasoning.match, value: formatMatch(metadata.reasoning_route_match) },
  ]

  return (
    <div className="mt-4 rounded-xl border border-violet-200/60 bg-violet-50/40 px-4 py-3">
      <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-violet-800/80">
        {es.reasoning.title}
      </p>
      <dl className="mt-3 grid gap-3 sm:grid-cols-2">
        {rows.map((row) => (
          <div key={row.label}>
            <dt className="text-[10px] uppercase tracking-[0.12em] text-muted-light">{row.label}</dt>
            <dd className="mt-1 text-[13px] font-medium text-foreground/85">{row.value}</dd>
          </div>
        ))}
      </dl>
    </div>
  )
}
