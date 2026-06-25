import type { CanonicalStatistics } from '../../types/canonicalEntities'
import { es } from '../../i18n/spanish'

export function CanonicalStatisticsSection({
  statistics,
  isLoading,
}: {
  statistics: CanonicalStatistics | null
  isLoading: boolean
}) {
  if (isLoading && !statistics) return <p className="text-sm text-muted">{es.common.loading}</p>
  if (!statistics) return <p className="text-sm text-muted">{es.common.noData}</p>

  const cards = [
    { label: es.canonicalEntities.stats.total, value: statistics.canonical_entities_total },
    { label: es.canonicalEntities.stats.matches, value: statistics.canonical_matches },
    { label: es.canonicalEntities.stats.pending, value: statistics.pending_matches },
    { label: es.canonicalEntities.stats.suggestions, value: statistics.automatic_suggestions },
    { label: es.canonicalEntities.stats.unresolved, value: `${statistics.unresolved_pct}%` },
  ]

  return (
    <section>
      <h2 className="text-[15px] font-semibold text-foreground">{es.canonicalEntities.stats.title}</h2>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {cards.map((card) => (
          <div key={card.label} className="rounded-xl border border-border-subtle bg-surface-elevated px-4 py-3">
            <p className="text-[11px] uppercase tracking-wide text-muted-light">{card.label}</p>
            <p className="mt-2 text-xl font-semibold tabular-nums">{card.value}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
