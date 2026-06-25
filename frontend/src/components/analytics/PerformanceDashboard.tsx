import type { PerformanceAnalytics } from '../../types/businessAnalytics'
import { es, getMetricTooltip } from '../../i18n/spanish'
import { AnalyticsCard } from './AnalyticsCard'

function formatMs(ms: number): string {
  if (ms >= 1000) return `${(ms / 1000).toFixed(1)} s`
  return `${ms.toFixed(1)} ms`
}

interface PerformanceDashboardProps {
  performance: PerformanceAnalytics | null
  isLoading?: boolean
}

export function PerformanceDashboard({
  performance,
  isLoading = false,
}: PerformanceDashboardProps) {
  const cards = performance
    ? [
        { label: es.analytics.performance.p50, value: formatMs(performance.p50_ms) },
        { label: es.analytics.performance.p95, value: formatMs(performance.p95_ms) },
        { label: es.analytics.performance.p99, value: formatMs(performance.p99_ms) },
        {
          label: es.analytics.performance.avgTotalTime,
          value: formatMs(performance.avg_total_ms),
          tooltip: getMetricTooltip('avgResponseTime'),
        },
      ]
    : []

  return (
    <section>
      <h2 className="text-lg font-semibold text-foreground">{es.analytics.performance.title}</h2>
      <p className="mt-1 text-[13px] text-muted">{es.analytics.performance.subtitle}</p>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {isLoading && !performance
          ? Array.from({ length: 4 }).map((_, index) => (
              <div
                key={index}
                className="animate-pulse rounded-2xl border border-border-subtle bg-surface-elevated px-4 py-5"
              >
                <div className="h-3 w-16 rounded bg-surface-subtle" />
                <div className="mt-4 h-8 w-20 rounded bg-surface-subtle" />
              </div>
            ))
          : cards.map((card) => <AnalyticsCard key={card.label} {...card} />)}
      </div>
    </section>
  )
}
