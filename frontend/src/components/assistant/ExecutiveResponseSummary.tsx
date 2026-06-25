import type { ChatMessage } from '../../types/chat'
import { es, translateHandledBy, translateQueryType } from '../../i18n/spanish'

interface ExecutiveResponseSummaryProps {
  message: ChatMessage
}

function formatConfidence(value?: number): string {
  if (value === undefined) return '—'
  return `${(value * 100).toFixed(0)}%`
}

function formatResponseTime(message: ChatMessage): string {
  const metadataMs = message.hybrid?.rawMetadata?.response_time_ms
  if (typeof metadataMs === 'number') return `${Math.round(metadataMs)} ms`
  if (message.timings?.total_ms !== undefined) {
    return `${Math.round(message.timings.total_ms)} ms`
  }
  return '—'
}

function readStringArray(metadata: Record<string, unknown>, key: string): string[] {
  const value = metadata[key]
  if (!Array.isArray(value)) return []
  return value.filter((item): item is string => typeof item === 'string' && item.length > 0)
}

function resolveEvidence(message: ChatMessage): string {
  const metadata = message.hybrid?.rawMetadata ?? {}
  const citations = readStringArray(metadata, 'evidence_sources')
  if (citations.length > 0) return citations.join(' · ')

  const packageId = metadata.evidence_package_id
  if (typeof packageId === 'string' && packageId) {
    return `Paquete de evidencia ${packageId}`
  }

  const queryType = message.hybrid?.queryType ?? message.intent
  if (queryType && queryType !== 'PRODUCT_IDENTITY') {
    return translateQueryType(queryType)
  }

  if (message.sources?.length) {
    return message.sources.join(' · ')
  }

  if (message.hybrid?.handledBy === 'product_identity') {
    return 'Identidad y capacidades del asistente'
  }

  return 'Datos corporativos estructurados'
}

function resolveLimitations(message: ChatMessage): string {
  const metadata = message.hybrid?.rawMetadata ?? {}
  const limitations = readStringArray(metadata, 'limitations')
  if (limitations.length > 0) return limitations.join(' · ')

  if (metadata.hallucination_guard_triggered === true) {
    return 'La evidencia disponible no fue suficiente para una síntesis completa.'
  }

  const confidence = message.hybrid?.confidence ?? message.intentConfidence
  if (confidence !== undefined && confidence < 0.6) {
    return 'Confianza moderada: conviene validar con el equipo de negocio.'
  }

  return 'Sin limitaciones reportadas para esta consulta.'
}

export function ExecutiveResponseSummary({ message }: ExecutiveResponseSummaryProps) {
  const handledBy = message.hybrid?.handledBy
  if (!handledBy) return null

  const rows = [
    {
      label: es.executiveSummary.channel,
      value: translateHandledBy(handledBy),
      tooltip: es.executiveSummary.channelTooltip,
    },
    {
      label: es.executiveSummary.confidence,
      value: formatConfidence(message.hybrid?.confidence ?? message.intentConfidence),
      tooltip: es.executiveSummary.confidenceTooltip,
    },
    {
      label: es.executiveSummary.evidence,
      value: resolveEvidence(message),
      tooltip: es.executiveSummary.evidenceTooltip,
      full: true,
    },
    {
      label: es.executiveSummary.limitations,
      value: resolveLimitations(message),
      tooltip: es.executiveSummary.limitationsTooltip,
      full: true,
    },
    {
      label: es.executiveSummary.responseTime,
      value: formatResponseTime(message),
      tooltip: es.executiveSummary.responseTimeTooltip,
    },
  ]

  return (
    <div className="mb-4 rounded-xl border border-border-subtle bg-surface-subtle/50 px-4 py-3">
      <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-muted-light">
        {es.executiveSummary.title}
      </p>
      <dl className="mt-3 grid gap-3 sm:grid-cols-2">
        {rows.map((row) => (
          <div key={row.label} className={row.full ? 'sm:col-span-2' : undefined} title={row.tooltip}>
            <dt className="text-[10px] uppercase tracking-[0.12em] text-muted-light">{row.label}</dt>
            <dd className="mt-1 text-[13px] font-medium text-foreground/85">{row.value}</dd>
          </div>
        ))}
      </dl>
    </div>
  )
}
