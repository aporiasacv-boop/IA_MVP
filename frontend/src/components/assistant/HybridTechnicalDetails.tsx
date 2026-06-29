import { useState } from 'react'
import type { ChatMessage } from '../../types/chat'
import { es, resolveGatewayRouteLabel, translateHandledBy, translateQueryType } from '../../i18n/spanish'

interface HybridTechnicalDetailsProps {
  message: ChatMessage
}

function formatConfidence(value?: number): string {
  if (value === undefined) return '—'
  return `${(value * 100).toFixed(0)}%`
}

export function HybridTechnicalDetails({ message }: HybridTechnicalDetailsProps) {
  const [open, setOpen] = useState(false)
  const hybrid = message.hybrid

  if (!hybrid) return null

  const rows = [
    {
      label: es.chat.gatewayRoute,
      value: resolveGatewayRouteLabel(hybrid.rawMetadata, hybrid.handledBy),
    },
    { label: es.chat.pipeline, value: translateHandledBy(hybrid.handledBy) },
    {
      label: es.chat.queryType,
      value: translateQueryType(hybrid.queryType ?? message.intent),
    },
    { label: es.chat.confidence, value: formatConfidence(hybrid.confidence) },
    ...(hybrid.sessionId
      ? [{ label: es.chat.sessionId, value: hybrid.sessionId }]
      : []),
    {
      label: es.chat.pendingClarification,
      value: hybrid.pendingClarification ? 'Sí' : 'No',
    },
    {
      label: es.chat.clarificationResolved,
      value:
        hybrid.clarificationResolved === undefined
          ? '—'
          : hybrid.clarificationResolved
            ? 'Sí'
            : 'No',
    },
  ]

  return (
    <div className="mt-5">
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className="transition-premium text-[12px] text-muted-light hover:text-muted"
      >
        {open ? '▾' : '▸'} {es.chat.technicalInfo}
      </button>

      {open && (
        <div className="animate-fade-in-up mt-3 rounded-xl border border-border-subtle bg-surface-subtle/70 px-4 py-4">
          <dl className="grid gap-3 sm:grid-cols-3">
            {rows.map((row) => (
              <div key={row.label}>
                <dt className="text-[10px] uppercase tracking-[0.12em] text-muted-light">
                  {row.label}
                </dt>
                <dd className="mt-1 text-[13px] font-medium text-foreground/85">{row.value}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}
    </div>
  )
}
