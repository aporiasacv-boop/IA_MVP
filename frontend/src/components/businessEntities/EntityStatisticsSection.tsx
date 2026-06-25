import type { BusinessEntityStatistics } from '../../types/businessEntities'
import { es } from '../../i18n/spanish'

interface Props {
  statistics: BusinessEntityStatistics | null
  isLoading: boolean
}

export function EntityStatisticsSection({ statistics, isLoading }: Props) {
  if (isLoading && !statistics) {
    return <p className="text-sm text-muted">{es.common.loading}</p>
  }
  if (!statistics) {
    return <p className="text-sm text-muted">{es.common.noData}</p>
  }

  const cards = [
    { label: es.businessEntities.stats.total, value: statistics.business_entities_total },
    { label: es.businessEntities.stats.loaded, value: statistics.business_entities_loaded },
    { label: es.businessEntities.stats.duplicated, value: statistics.duplicated_entities },
  ]

  return (
    <section>
      <h2 className="text-[15px] font-semibold text-foreground">{es.businessEntities.stats.title}</h2>
      <p className="mt-1 text-[12px] text-muted">{es.businessEntities.stats.subtitle}</p>
      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        {cards.map((card) => (
          <div
            key={card.label}
            className="rounded-xl border border-border-subtle bg-surface-elevated px-4 py-3"
          >
            <p className="text-[11px] uppercase tracking-wide text-muted-light">{card.label}</p>
            <p className="mt-2 text-xl font-semibold tabular-nums text-foreground">{card.value}</p>
          </div>
        ))}
      </div>
      {statistics.last_entity_refresh && (
        <p className="mt-3 text-[11px] text-muted-light">
          {es.businessEntities.stats.lastRefresh}:{' '}
          {new Date(statistics.last_entity_refresh).toLocaleString('es-MX')}
        </p>
      )}
    </section>
  )
}
