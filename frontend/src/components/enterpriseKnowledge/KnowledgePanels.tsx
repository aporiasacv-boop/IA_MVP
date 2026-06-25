import type { EnterpriseKnowledgeObject, KnowledgeItem, KnowledgeListItem } from '../../types/enterpriseKnowledge'
import { es } from '../../i18n/spanish'

interface ListProps {
  items: KnowledgeListItem[]
  selectedId?: number
  isLoading: boolean
  onSelect: (canonicalId: number) => void
}

export function KnowledgeEntityList({ items, selectedId, isLoading, onSelect }: ListProps) {
  return (
    <section>
      <h2 className="text-[13px] font-semibold">{es.enterpriseKnowledge.list.title}</h2>
      <div className="mt-4 overflow-x-auto rounded-xl border border-border-subtle">
        <table className="min-w-full text-left text-[12px]">
          <thead className="border-b border-border-subtle bg-surface-elevated text-muted">
            <tr>
              <th className="px-3 py-2">{es.enterpriseKnowledge.table.entity}</th>
              <th className="px-3 py-2">{es.enterpriseKnowledge.table.completeness}</th>
              <th className="px-3 py-2">{es.enterpriseKnowledge.table.confidence}</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={3} className="px-3 py-6 text-center text-muted">
                  {es.common.loading}
                </td>
              </tr>
            ) : items.length === 0 ? (
              <tr>
                <td colSpan={3} className="px-3 py-6 text-center text-muted">
                  {es.common.noData}
                </td>
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
                  <td className="px-3 py-2 tabular-nums">
                    {(parseFloat(item.completeness) * 100).toFixed(0)}%
                  </td>
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
  entity: EnterpriseKnowledgeObject | null
}

export function KnowledgeDetailPanel({ entity }: DetailProps) {
  if (!entity) {
    return <p className="text-[12px] text-muted">{es.enterpriseKnowledge.detail.empty}</p>
  }

  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-[13px] font-semibold">{es.enterpriseKnowledge.detail.title}</h2>
        <p className="mt-1 text-lg font-semibold">{entity.identity.canonical_name}</p>
        <p className="text-[12px] text-muted">
          {entity.identity.normalized_name}
          {entity.identity.primary_rfc ? ` · RFC ${entity.identity.primary_rfc}` : ''}
        </p>
        <p className="mt-1 text-[11px] text-muted-light">
          {es.enterpriseKnowledge.detail.completeness}:{' '}
          {(parseFloat(entity.quality.completeness) * 100).toFixed(1)}% ·{' '}
          {es.enterpriseKnowledge.detail.confidence}:{' '}
          {(parseFloat(entity.quality.average_confidence) * 100).toFixed(1)}%
        </p>
      </div>

      <KnowledgeSection title={es.enterpriseKnowledge.sections.identity} items={entity.identity.items} />
      <KnowledgeSection title={es.enterpriseKnowledge.sections.ontology} items={[...entity.roles, ...entity.nature, ...entity.behaviors]} />
      <KnowledgeSection title={es.enterpriseKnowledge.sections.facts} items={entity.facts} />
      <KnowledgeSection title={es.enterpriseKnowledge.sections.signals} items={entity.signals} />
      <KnowledgeSection title={es.enterpriseKnowledge.sections.alerts} items={entity.alerts} highlight />
      <KnowledgeSection title={es.enterpriseKnowledge.sections.relationships} items={entity.relationships} />
      <EvidenceSection evidence={entity.evidence} />
    </section>
  )
}

function KnowledgeSection({
  title,
  items,
  highlight = false,
}: {
  title: string
  items: KnowledgeItem[]
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
              <th className="px-2 py-1.5">{es.enterpriseKnowledge.table.key}</th>
              <th className="px-2 py-1.5">{es.enterpriseKnowledge.table.value}</th>
              <th className="px-2 py-1.5">{es.enterpriseKnowledge.table.source}</th>
              <th className="px-2 py-1.5">{es.enterpriseKnowledge.table.confidence}</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr
                key={`${item.key}-${item.computed_at}`}
                className={`border-t border-border-subtle/60 ${highlight ? 'bg-amber-50/50' : ''}`}
              >
                <td className="px-2 py-1.5 font-medium">{item.key}</td>
                <td className="px-2 py-1.5 max-w-[200px] truncate font-mono text-[10px]">
                  {formatValue(item.value)}
                </td>
                <td className="px-2 py-1.5 text-muted">{item.source}</td>
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
      <h3 className="text-[12px] font-semibold">{es.enterpriseKnowledge.sections.evidence}</h3>
      <pre className="mt-2 max-h-40 overflow-auto rounded-lg border border-border-subtle bg-surface-elevated p-3 text-[10px]">
        {JSON.stringify(evidence, null, 2)}
      </pre>
    </div>
  )
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return '—'
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

interface StatsProps {
  statistics: {
    knowledge_objects_total: number
    knowledge_average_completeness: number
    knowledge_average_confidence: number
    incomplete_objects: number
  } | null
  isLoading: boolean
}

export function KnowledgeStatisticsSection({ statistics, isLoading }: StatsProps) {
  const cards = [
    { label: es.enterpriseKnowledge.stats.objects, value: statistics?.knowledge_objects_total ?? '—' },
    {
      label: es.enterpriseKnowledge.stats.completeness,
      value: statistics ? `${(statistics.knowledge_average_completeness * 100).toFixed(1)}%` : '—',
    },
    {
      label: es.enterpriseKnowledge.stats.confidence,
      value: statistics ? `${(statistics.knowledge_average_confidence * 100).toFixed(1)}%` : '—',
    },
    { label: es.enterpriseKnowledge.stats.incomplete, value: statistics?.incomplete_objects ?? '—' },
  ]

  return (
    <section>
      <h2 className="text-[13px] font-semibold">{es.enterpriseKnowledge.stats.title}</h2>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
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
