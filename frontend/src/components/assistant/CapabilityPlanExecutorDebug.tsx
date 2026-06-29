import type { ChatMessage } from '../../types/chat'
import { es } from '../../i18n/spanish'

interface CapabilityPlanExecutorDebugProps {
  message: ChatMessage
}

function formatBool(value: unknown): string {
  if (value === true) return 'Sí'
  if (value === false) return 'No'
  return '—'
}

export function CapabilityPlanExecutorDebug({ message }: CapabilityPlanExecutorDebugProps) {
  const metadata = message.hybrid?.rawMetadata
  if (!metadata || metadata.plan_executed === undefined) return null

  const rows = [
    { label: es.planExecutor.strategy, value: String(metadata.execution_strategy ?? '—') },
    { label: es.planExecutor.capability, value: String(metadata.primary_capability ?? '—') },
    {
      label: es.planExecutor.coverage,
      value:
        typeof metadata.coverage_used === 'number' ? `${metadata.coverage_used}%` : String(metadata.coverage_used ?? '—'),
    },
    { label: es.planExecutor.fallbackAvoided, value: formatBool(metadata.fallback_avoided) },
    {
      label: es.planExecutor.time,
      value:
        typeof metadata.execution_time_ms === 'number'
          ? `${metadata.execution_time_ms} ms`
          : String(metadata.execution_time_ms ?? '—'),
    },
  ]

  return (
    <div className="mt-4 rounded-xl border border-orange-200/70 bg-orange-50/40 px-4 py-3">
      <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-orange-900/80">
        {es.planExecutor.title}
      </p>
      <dl className="mt-3 grid gap-3 sm:grid-cols-2">
        {rows.map((row) => (
          <div key={row.label}>
            <dt className="text-[10px] uppercase tracking-[0.12em] text-muted-light">{row.label}</dt>
            <dd className="mt-1 text-[13px] font-medium text-foreground/85">{row.value}</dd>
          </div>
        ))}
      </dl>
      {metadata.partial_execution === true && (
        <p className="mt-2 text-[12px] text-muted">{es.planExecutor.partialNote}</p>
      )}
    </div>
  )
}
