import { es, translateReasoningRoute } from '../../i18n/spanish'
import type { ChatMessage } from '../../types/chat'

interface ReasoningGovernanceDebugProps {
  message: ChatMessage
}

function formatGoverned(value: unknown): string {
  if (value === true) return 'Sí'
  if (value === false) return 'No'
  return '—'
}

export function ReasoningGovernanceDebug({ message }: ReasoningGovernanceDebugProps) {
  const metadata = message.hybrid?.rawMetadata
  if (metadata?.governance_rule === undefined && metadata?.reasoning_governed === undefined) {
    return null
  }

  const rows = [
    {
      label: es.governance.decision,
      value: translateReasoningRoute(metadata.reasoning_route),
    },
    {
      label: es.governance.governed,
      value: formatGoverned(metadata.reasoning_governed),
    },
    {
      label: es.governance.fallback,
      value: metadata.governance_rule === 'fallback' ? 'Sí' : 'No',
    },
    {
      label: es.governance.pipelineSkipped,
      value: formatGoverned(metadata.pipeline_skipped),
    },
    {
      label: es.governance.rule,
      value: String(metadata.governance_rule ?? '—'),
    },
  ]

  return (
    <div className="mt-4 rounded-xl border border-emerald-200/60 bg-emerald-50/40 px-4 py-3">
      <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-emerald-800/80">
        {es.governance.title}
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
