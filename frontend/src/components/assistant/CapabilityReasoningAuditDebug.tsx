import type { ChatMessage } from '../../types/chat'
import { es, translateReasoningRoute } from '../../i18n/spanish'

interface CapabilityAuditPayload {
  intent?: string | null
  confidence?: number | null
  explanation?: string | null
  decision?: {
    selected_capability?: string
    final_route?: string
    fallback_used?: boolean
    reason?: string
  }
  evaluation?: {
    classification?: string
    summary?: string
    reusable_capabilities_exist?: boolean
    could_combine_capabilities?: boolean
    notes?: string[]
  }
  report_text?: string
}

interface CapabilityReasoningAuditDebugProps {
  message: ChatMessage
}

function readAuditPayload(message: ChatMessage): CapabilityAuditPayload | null {
  const raw = message.hybrid?.rawMetadata?.capability_reasoning_audit
  if (!raw || typeof raw !== 'object') return null
  return raw as CapabilityAuditPayload
}

export function CapabilityReasoningAuditDebug({ message }: CapabilityReasoningAuditDebugProps) {
  const metadata = message.hybrid?.rawMetadata
  const audit = readAuditPayload(message)
  if (!audit) return null

  const rows = [
    {
      label: es.capabilityAudit.intent,
      value: audit.intent ?? metadata?.reasoning_intent ?? '—',
    },
    {
      label: es.capabilityAudit.selectedCapability,
      value: String(metadata?.audit_selected_capability ?? audit.decision?.selected_capability ?? '—'),
    },
    {
      label: es.capabilityAudit.finalRoute,
      value: translateReasoningRoute(
        metadata?.audit_final_route ?? audit.decision?.final_route ?? '—',
      ),
    },
    {
      label: es.capabilityAudit.evaluation,
      value: audit.evaluation?.classification ?? '—',
    },
  ]

  return (
    <div className="mt-4 rounded-xl border border-violet-200/70 bg-violet-50/40 px-4 py-3">
      <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-violet-900/80">
        {es.capabilityAudit.title}
      </p>
      <dl className="mt-3 grid gap-3 sm:grid-cols-2">
        {rows.map((row) => (
          <div key={row.label}>
            <dt className="text-[10px] uppercase tracking-[0.12em] text-muted-light">{row.label}</dt>
            <dd className="mt-1 text-[13px] font-medium text-foreground/85">{row.value}</dd>
          </div>
        ))}
      </dl>
      {audit.evaluation?.summary && (
        <p className="mt-3 text-[13px] leading-6 text-foreground/85">{audit.evaluation.summary}</p>
      )}
      {audit.evaluation?.notes && audit.evaluation.notes.length > 0 && (
        <ul className="mt-2 list-disc space-y-1 pl-5 text-[12px] text-muted">
          {audit.evaluation.notes.map((note) => (
            <li key={note}>{note}</li>
          ))}
        </ul>
      )}
      {audit.report_text && (
        <pre className="mt-3 max-h-56 overflow-auto rounded-lg bg-white/70 p-3 text-[11px] leading-5 text-foreground/80">
          {audit.report_text}
        </pre>
      )}
    </div>
  )
}
