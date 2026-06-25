import type { BackendMetricsData } from '../../hooks/useBackendMetrics'
import { es } from '../../i18n/spanish'

interface BackendMetricsSectionProps {
  data: BackendMetricsData | null
  isLoading?: boolean
  error?: string | null
  onRefresh?: () => void
}

const formatter = new Intl.NumberFormat('es-MX')

function formatMs(ms: number): string {
  if (ms >= 1000) return `${(ms / 1000).toFixed(1)} s`
  return `${ms.toFixed(1)} ms`
}

function pct(part: number, total: number): string {
  if (total === 0) return '0.0'
  return ((part / total) * 100).toFixed(1)
}

export function BackendMetricsSection({
  data,
  isLoading = false,
  error,
  onRefresh,
}: BackendMetricsSectionProps) {
  const summary = data?.summary
  const performance = data?.performance
  const topQueries = data?.topQueries ?? []

  const pipelinePct = summary ? pct(summary.business_pipeline_requests, summary.total_requests) : '0.0'
  const legacyPct = summary ? pct(summary.legacy_chat_requests, summary.total_requests) : '0.0'
  const guidedFallbackPct = summary
    ? pct(summary.guided_fallback_requests ?? 0, summary.total_requests)
    : '0.0'
  const capabilityDiscoveryPct = summary
    ? pct(summary.capability_discovery_requests ?? 0, summary.total_requests)
    : '0.0'
  const suggestionsPct = summary
    ? pct(summary.suggested_questions_generated ?? 0, summary.total_requests)
    : '0.0'

  const summaryCards = summary
    ? [
        {
          label: es.performance.totalRequests,
          value: formatter.format(summary.total_requests),
        },
        {
          label: es.performance.businessPipelineRequests,
          value: formatter.format(summary.business_pipeline_requests),
          sub: `${pipelinePct}%`,
        },
        {
          label: es.performance.legacyChatRequests,
          value: formatter.format(summary.legacy_chat_requests),
          sub: `${legacyPct}%`,
        },
        {
          label: es.performance.guidedFallbackRequests,
          value: formatter.format(summary.guided_fallback_requests ?? 0),
          sub: `${guidedFallbackPct}%`,
        },
        {
          label: es.performance.capabilityDiscoveryRequests,
          value: formatter.format(summary.capability_discovery_requests ?? 0),
          sub: `${capabilityDiscoveryPct}%`,
        },
        {
          label: es.performance.suggestedQuestionsGenerated,
          value: formatter.format(summary.suggested_questions_generated ?? 0),
          sub: `${suggestionsPct}%`,
        },
        {
          label: es.performance.avgSuggestionsPerResponse,
          value: (summary.average_suggestions_per_response ?? 0).toFixed(1),
        },
        { label: es.performance.pipelinePct, value: `${pipelinePct}%` },
        { label: es.performance.legacyPct, value: `${legacyPct}%` },
      ]
    : []

  const percentileCards = performance
    ? [
        { label: es.analytics.performance.p50, value: formatMs(performance.p50_total_time_ms) },
        { label: es.analytics.performance.p95, value: formatMs(performance.p95_total_time_ms) },
        { label: es.analytics.performance.p99, value: formatMs(performance.p99_total_time_ms) },
      ]
    : []

  return (
    <section className="border-t border-border-subtle px-4 py-8 md:px-8 md:py-10">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-muted-light">
            {es.performance.backendEyebrow}
          </p>
          <h2 className="mt-3 text-xl font-semibold tracking-[-0.03em] text-foreground md:text-2xl">
            {es.performance.backendTitle}
          </h2>
          <p className="mt-2 text-[13px] text-muted">{es.performance.backendSubtitle}</p>
        </div>
        {onRefresh && (
          <button
            type="button"
            onClick={() => onRefresh()}
            disabled={isLoading}
            className="transition-premium rounded-lg border border-border-subtle bg-surface-elevated px-3 py-2 text-[12px] font-medium text-muted hover:text-foreground disabled:opacity-50"
          >
            {isLoading ? es.common.loading : es.common.refresh}
          </button>
        )}
      </div>

      {error && (
        <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          {error}
        </div>
      )}

      <div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {isLoading && !summary
          ? Array.from({ length: 5 }).map((_, i) => (
              <div
                key={i}
                className="animate-pulse rounded-2xl border border-border-subtle bg-surface-elevated px-4 py-5"
              >
                <div className="h-3 w-20 rounded bg-surface-subtle" />
                <div className="mt-4 h-8 w-16 rounded bg-surface-subtle" />
              </div>
            ))
          : summaryCards.map((card) => (
              <div
                key={card.label}
                className="transition-premium rounded-2xl border border-olnatura-200 bg-olnatura-50/60 px-4 py-5"
              >
                <p className="text-[11px] text-muted-light">{card.label}</p>
                <p className="mt-2 text-2xl font-semibold tracking-[-0.02em] text-foreground">
                  {card.value}
                </p>
                {'sub' in card && card.sub && (
                  <p className="mt-1 text-[11px] text-olnatura-600">{card.sub}</p>
                )}
              </div>
            ))}
      </div>

      {percentileCards.length > 0 && (
        <div className="mt-6">
          <p className="text-[11px] font-medium uppercase tracking-[0.16em] text-muted-light">
            {es.performance.latencyTitle}
          </p>
          <div className="mt-3 grid gap-3 sm:grid-cols-3">
            {percentileCards.map((card) => (
              <div
                key={card.label}
                className="rounded-2xl border border-border-subtle bg-surface-elevated px-4 py-4"
              >
                <p className="text-[11px] text-muted-light">{card.label}</p>
                <p className="mt-2 text-xl font-semibold text-foreground">{card.value}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mt-8">
        <p className="text-[11px] font-medium uppercase tracking-[0.16em] text-muted-light">
          {es.performance.topQueries}
        </p>
        {topQueries.length === 0 && !isLoading ? (
          <p className="mt-3 text-[13px] text-muted">{es.common.noData}</p>
        ) : (
          <ol className="mt-3 divide-y divide-border-subtle rounded-2xl border border-border-subtle bg-surface-elevated">
            {topQueries.map((item, index) => (
              <li
                key={`${item.question}-${index}`}
                className="flex items-start justify-between gap-4 px-4 py-3 text-[13px]"
              >
                <span className="text-foreground/90">{item.question}</span>
                <span className="shrink-0 font-medium text-muted">{formatter.format(item.count)}</span>
              </li>
            ))}
          </ol>
        )}
      </div>
    </section>
  )
}
