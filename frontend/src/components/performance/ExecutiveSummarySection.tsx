import type { PerformanceMetrics } from '../../types/performance'
import { es } from '../../i18n/spanish'

interface ExecutiveSummarySectionProps {
  metrics: PerformanceMetrics | null
  isLoading?: boolean
  onRefresh?: () => void
}

const formatter = new Intl.NumberFormat('es-MX')

function formatMs(ms: number): string {
  if (ms >= 1000) return `${(ms / 1000).toFixed(1)} s`
  return `${ms.toFixed(1)} ms`
}

export function ExecutiveSummarySection({
  metrics,
  isLoading = false,
  onRefresh,
}: ExecutiveSummarySectionProps) {
  const deterministicPct =
    metrics && metrics.totalQueries > 0
      ? ((metrics.deterministicQueries / metrics.totalQueries) * 100).toFixed(1)
      : '0.0'

  const cards = metrics
    ? [
        {
          label: es.performance.totalQueries,
          value: formatter.format(metrics.totalQueries),
          accent: false,
        },
        {
          label: es.performance.deterministicQueries,
          value: formatter.format(metrics.deterministicQueries),
          sub: `${deterministicPct}% del total`,
          accent: true,
        },
        {
          label: es.performance.generativeQueries,
          value: formatter.format(metrics.generativeQueries),
          accent: false,
        },
        {
          label: es.performance.estimatedSavings,
          value: `$${metrics.estimatedCostAvoidedUsd.toFixed(0)} USD`,
          accent: true,
        },
        {
          label: es.performance.averageTime,
          value: formatMs(metrics.averageResponseMs),
          sub: es.performance.responseToUser,
          accent: false,
        },
      ]
    : []

  return (
    <section className="px-4 py-8 md:px-8 md:py-10">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-muted-light">
            {es.performance.localMetricsEyebrow}
          </p>
          <h1 className="mt-3 text-2xl font-semibold tracking-[-0.03em] text-foreground md:text-[1.75rem]">
            {es.performance.platformPerformanceTitle}
          </h1>
          <p className="mt-2 text-[13px] text-muted">{es.performance.localMetricsSubtitle}</p>
        </div>
        {onRefresh && (
          <button
            type="button"
            onClick={() => onRefresh()}
            disabled={isLoading}
            className="transition-premium rounded-lg border border-border-subtle bg-surface-elevated px-3 py-2 text-[12px] font-medium text-muted hover:text-foreground disabled:opacity-50"
          >
            {isLoading ? es.performance.measuring : es.common.refresh}
          </button>
        )}
      </div>

      <div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {isLoading && !metrics
          ? Array.from({ length: 5 }).map((_, i) => (
              <div
                key={i}
                className="animate-pulse rounded-2xl border border-border-subtle bg-surface-elevated px-4 py-5"
              >
                <div className="h-3 w-20 rounded bg-surface-subtle" />
                <div className="mt-4 h-8 w-16 rounded bg-surface-subtle" />
              </div>
            ))
          : cards.map((card) => (
              <div
                key={card.label}
                className={[
                  'transition-premium rounded-2xl border px-4 py-5',
                  card.accent
                    ? 'border-olnatura-200 bg-olnatura-50/80'
                    : 'border-border-subtle bg-surface-elevated',
                ].join(' ')}
              >
                <p className="text-[11px] text-muted-light">{card.label}</p>
                <p className="mt-2 text-2xl font-semibold tracking-[-0.02em] text-foreground">
                  {card.value}
                </p>
                {card.sub && (
                  <p className="mt-1 text-[11px] text-olnatura-600">{card.sub}</p>
                )}
              </div>
            ))}
      </div>
    </section>
  )
}
