import type { OntologyStatistics } from '../../types/businessOntology'
import { es } from '../../i18n/spanish'

interface Props {
  statistics: OntologyStatistics | null
  isLoading: boolean
}

export function OntologyStatisticsSection({ statistics, isLoading }: Props) {
  const cards = [
    { label: es.businessOntology.stats.entities, value: statistics?.ontology_entities ?? '—' },
    { label: es.businessOntology.stats.pending, value: statistics?.ontology_pending ?? '—' },
    { label: es.businessOntology.stats.approved, value: statistics?.ontology_approved ?? '—' },
    { label: es.businessOntology.stats.rules, value: statistics?.ontology_rules ?? '—' },
    {
      label: es.businessOntology.stats.confidence,
      value: statistics ? `${(statistics.ontology_average_confidence * 100).toFixed(1)}%` : '—',
    },
    { label: es.businessOntology.stats.withoutSuggestions, value: statistics?.entities_without_suggestions ?? '—' },
  ]

  return (
    <section>
      <h2 className="text-[13px] font-semibold">{es.businessOntology.stats.title}</h2>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {cards.map((card) => (
          <div key={card.label} className="rounded-xl border border-border-subtle bg-surface-elevated px-4 py-3">
            <p className="text-[11px] text-muted">{card.label}</p>
            <p className="mt-1 text-lg font-semibold tabular-nums">{isLoading ? '…' : card.value}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
