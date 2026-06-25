import type { PerformanceMetrics } from '../../types/performance'
import { es } from '../../i18n/spanish'

interface PerformanceMetricsGridProps {
  metrics: PerformanceMetrics
}

const formatter = new Intl.NumberFormat('es-MX')

const METRIC_NARRATIVES: Record<string, string> = {
  [es.performance.totalQueries]: es.performance.metricNarratives.totalQueries,
  [es.performance.deterministicQueries]: es.performance.metricNarratives.deterministicQueries,
  [es.performance.generativeQueries]: es.performance.metricNarratives.generativeQueries,
  [es.performance.averageTime]: es.performance.metricNarratives.averageTime,
  [es.performance.tokensSaved]: es.performance.metricNarratives.tokensSaved,
  [es.performance.estimatedCostAvoided]: es.performance.metricNarratives.estimatedCostAvoided,
  [es.performance.llmCallsAvoided]: es.performance.metricNarratives.llmCallsAvoided,
}

export function PerformanceMetricsGrid({ metrics }: PerformanceMetricsGridProps) {
  const deterministicShare =
    (metrics.deterministicQueries / metrics.totalQueries) * 100

  const rows = [
    { label: es.performance.totalQueries, value: formatter.format(metrics.totalQueries) },
    {
      label: es.performance.deterministicQueries,
      value: `${formatter.format(metrics.deterministicQueries)} · ${deterministicShare.toFixed(1)}%`,
    },
    { label: es.performance.generativeQueries, value: formatter.format(metrics.generativeQueries) },
    { label: es.performance.averageTime, value: `${metrics.averageResponseMs.toFixed(1)} ms` },
    { label: es.performance.tokensSaved, value: formatter.format(metrics.tokensSaved) },
    {
      label: es.performance.estimatedCostAvoided,
      value: `$${metrics.estimatedCostAvoidedUsd.toFixed(2)} USD`,
    },
    {
      label: es.performance.llmCallsAvoided,
      value: formatter.format(metrics.llmCallsAvoided),
    },
  ]

  return (
    <section className="mx-auto max-w-4xl px-6 py-8 md:px-12 md:py-10">
      <p className="text-[11px] font-medium uppercase tracking-[0.16em] text-muted-light">
        {es.performance.efficiencyIndicators}
      </p>

      <div className="mt-5 divide-y divide-border-subtle">
        {rows.map((row) => (
          <div
            key={row.label}
            className="transition-premium flex flex-col gap-1 py-5 sm:flex-row sm:items-end sm:justify-between"
          >
            <div>
              <p className="text-sm font-medium text-foreground/90">{row.label}</p>
              <p className="mt-1 text-[12px] text-muted-light">
                {METRIC_NARRATIVES[row.label]}
              </p>
            </div>
            <p className="text-xl font-semibold tracking-[-0.02em] text-foreground sm:text-right">
              {row.value}
            </p>
          </div>
        ))}
      </div>
    </section>
  )
}
