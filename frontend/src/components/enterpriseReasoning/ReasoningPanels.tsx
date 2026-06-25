import type { EnterpriseReasoningObject, ReasoningConclusion, ReasoningListItem } from '../../types/enterpriseReasoning'
import { es } from '../../i18n/spanish'

const SEVERITY_COLORS: Record<string, string> = {
  low: '',
  medium: 'bg-amber-50/50',
  high: 'bg-orange-50/60',
  critical: 'bg-red-50/60',
}

interface ListProps {
  items: ReasoningListItem[]
  selectedId?: number
  isLoading: boolean
  onSelect: (canonicalId: number) => void
}

export function ReasoningEntityList({ items, selectedId, isLoading, onSelect }: ListProps) {
  return (
    <section>
      <h2 className="text-[13px] font-semibold">{es.enterpriseReasoning.list.title}</h2>
      <div className="mt-4 overflow-x-auto rounded-xl border border-border-subtle">
        <table className="min-w-full text-left text-[12px]">
          <thead className="border-b border-border-subtle bg-surface-elevated text-muted">
            <tr>
              <th className="px-3 py-2">{es.enterpriseReasoning.table.entity}</th>
              <th className="px-3 py-2">{es.enterpriseReasoning.table.findings}</th>
              <th className="px-3 py-2">{es.enterpriseReasoning.table.confidence}</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={3} className="px-3 py-6 text-center text-muted">{es.common.loading}</td>
              </tr>
            ) : items.length === 0 ? (
              <tr>
                <td colSpan={3} className="px-3 py-6 text-center text-muted">{es.common.noData}</td>
              </tr>
            ) : (
              items.map((item) => (
                <tr
                  key={item.canonical_id}
                  onClick={() => onSelect(item.canonical_id)}
                  className={`cursor-pointer border-b border-border-subtle/60 hover:bg-surface-elevated/60 ${
                    selectedId === item.canonical_id ? 'bg-surface-elevated' : ''
                  }`}
                >
                  <td className="px-3 py-2 font-medium">{item.canonical_name}</td>
                  <td className="px-3 py-2 tabular-nums">{item.findings_count}</td>
                  <td className="px-3 py-2 tabular-nums">
                    {(parseFloat(item.average_confidence) * 100).toFixed(0)}%
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  )
}

interface DetailProps {
  entity: EnterpriseReasoningObject | null
}

export function ReasoningDetailPanel({ entity }: DetailProps) {
  if (!entity) {
    return <p className="text-[12px] text-muted">{es.enterpriseReasoning.detail.empty}</p>
  }

  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-[13px] font-semibold">{es.enterpriseReasoning.detail.title}</h2>
        <p className="mt-1 text-[12px] text-muted">
          {es.enterpriseReasoning.detail.confidence}:{' '}
          {(parseFloat(entity.confidence.average_confidence) * 100).toFixed(1)}% ·{' '}
          {es.enterpriseReasoning.detail.rules}: {entity.confidence.rules_executed}
        </p>
      </div>

      <ConclusionSection title={es.enterpriseReasoning.sections.findings} items={entity.findings} />
      <ConclusionSection title={es.enterpriseReasoning.sections.signals} items={entity.signals} />
      <ConclusionSection title={es.enterpriseReasoning.sections.alerts} items={entity.alerts} highlight />
      <ConclusionSection title={es.enterpriseReasoning.sections.risks} items={entity.risks} highlight />
      <ConclusionSection title={es.enterpriseReasoning.sections.opportunities} items={entity.opportunities} />
      <ConclusionSection title={es.enterpriseReasoning.sections.recommendations} items={entity.recommendations} />
      <EvidenceSection evidence={entity.evidence} />
    </section>
  )
}

function ConclusionSection({
  title,
  items,
  highlight = false,
}: {
  title: string
  items: ReasoningConclusion[]
  highlight?: boolean
}) {
  if (items.length === 0) return null

  return (
    <div>
      <h3 className="text-[12px] font-semibold">{title}</h3>
      <div className="mt-2 overflow-x-auto rounded-lg border border-border-subtle">
        <table className="min-w-full text-left text-[11px]">
          <thead className="bg-surface-elevated text-muted">
            <tr>
              <th className="px-2 py-1.5">{es.enterpriseReasoning.table.key}</th>
              <th className="px-2 py-1.5">{es.enterpriseReasoning.table.rule}</th>
              <th className="px-2 py-1.5">{es.enterpriseReasoning.table.severity}</th>
              <th className="px-2 py-1.5">{es.enterpriseReasoning.table.confidence}</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr
                key={`${item.rule_code}-${item.key}`}
                className={`border-t border-border-subtle/60 ${highlight ? SEVERITY_COLORS[item.severity] ?? '' : ''}`}
              >
                <td className="px-2 py-1.5 font-medium">{item.key}</td>
                <td className="px-2 py-1.5 font-mono text-[10px]">{item.rule_code}</td>
                <td className="px-2 py-1.5">{item.severity}</td>
                <td className="px-2 py-1.5 tabular-nums">
                  {(parseFloat(item.confidence) * 100).toFixed(0)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function EvidenceSection({ evidence }: { evidence: Array<Record<string, unknown>> }) {
  if (evidence.length === 0) return null

  return (
    <div>
      <h3 className="text-[12px] font-semibold">{es.enterpriseReasoning.sections.evidence}</h3>
      <pre className="mt-2 max-h-40 overflow-auto rounded-lg border border-border-subtle bg-surface-elevated p-3 text-[10px]">
        {JSON.stringify(evidence, null, 2)}
      </pre>
    </div>
  )
}

interface StatsProps {
  statistics: ReasoningStatistics | null
  isLoading: boolean
}

type ReasoningStatistics = {
  reasoning_objects_total: number
  reasoning_rules_executed: number
  average_reasoning_confidence: number
  average_findings: number
  average_alerts: number
  average_recommendations: number
}

export function ReasoningStatisticsSection({ statistics, isLoading }: StatsProps) {
  const cards = [
    { label: es.enterpriseReasoning.stats.objects, value: statistics?.reasoning_objects_total ?? '—' },
    { label: es.enterpriseReasoning.stats.rules, value: statistics?.reasoning_rules_executed ?? '—' },
    {
      label: es.enterpriseReasoning.stats.confidence,
      value: statistics ? `${(statistics.average_reasoning_confidence * 100).toFixed(1)}%` : '—',
    },
    { label: es.enterpriseReasoning.stats.findings, value: statistics?.average_findings?.toFixed(1) ?? '—' },
    { label: es.enterpriseReasoning.stats.recommendations, value: statistics?.average_recommendations?.toFixed(1) ?? '—' },
  ]

  return (
    <section>
      <h2 className="text-[13px] font-semibold">{es.enterpriseReasoning.stats.title}</h2>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {cards.map((card) => (
          <div key={card.label} className="rounded-xl border border-border-subtle bg-surface-elevated px-4 py-3">
            <p className="text-[11px] text-muted">{card.label}</p>
            <p className="mt-1 text-xl font-semibold tabular-nums">
              {isLoading ? es.common.loading : card.value}
            </p>
          </div>
        ))}
      </div>
    </section>
  )
}
