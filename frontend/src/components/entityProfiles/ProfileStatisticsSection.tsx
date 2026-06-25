import type { EntityProfileStatistics } from '../../types/entityProfiles'
import { es } from '../../i18n/spanish'

function formatPct(value: number): string {
  return `${(value * 100).toFixed(1)}%`
}

interface Props {
  statistics: EntityProfileStatistics | null
  isLoading: boolean
}

export function ProfileStatisticsSection({ statistics, isLoading }: Props) {
  const cards = [
    { label: es.entityProfiles.stats.total, value: statistics?.entity_profiles_total ?? '—' },
    { label: es.entityProfiles.stats.completeness, value: statistics ? formatPct(statistics.average_profile_completeness) : '—' },
    { label: es.entityProfiles.stats.movements, value: statistics?.total_movements_profiled ?? '—' },
    { label: es.entityProfiles.stats.withoutMovements, value: statistics?.profiles_without_movements ?? '—' },
    { label: es.entityProfiles.stats.generationTime, value: statistics ? `${statistics.profile_generation_time}s` : '—' },
    { label: es.entityProfiles.stats.lastRefresh, value: statistics?.last_profile_refresh?.slice(0, 10) ?? '—' },
  ]

  return (
    <section>
      <h2 className="text-[13px] font-semibold">{es.entityProfiles.stats.title}</h2>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {cards.map((card) => (
          <div
            key={card.label}
            className="rounded-xl border border-border-subtle bg-surface-elevated px-4 py-3"
          >
            <p className="text-[11px] text-muted">{card.label}</p>
            <p className="mt-1 text-lg font-semibold tabular-nums">
              {isLoading ? '…' : card.value}
            </p>
          </div>
        ))}
      </div>
    </section>
  )
}
