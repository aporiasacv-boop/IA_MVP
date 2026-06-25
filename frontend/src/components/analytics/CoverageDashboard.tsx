import type { CoverageAnalytics } from '../../types/businessAnalytics'
import { es, getMetricTooltip } from '../../i18n/spanish'
import { AnalyticsCard } from './AnalyticsCard'

const formatter = new Intl.NumberFormat('es-MX')

interface CoverageDashboardProps {
  coverage: CoverageAnalytics | null
  isLoading?: boolean
}

export function CoverageDashboard({ coverage, isLoading = false }: CoverageDashboardProps) {
  const cards = coverage
    ? [
        {
          label: es.analytics.coverage.totalRequests,
          value: formatter.format(coverage.total_requests),
          tooltip: getMetricTooltip('totalRequests'),
        },
        {
          label: `${es.analytics.coverage.businessPipeline} %`,
          value: `${coverage.business_pipeline_pct.toFixed(1)}%`,
          tooltip: getMetricTooltip('businessPipelinePct'),
        },
        {
          label: `${es.analytics.coverage.memory} %`,
          value: `${coverage.conversation_memory_pct.toFixed(1)}%`,
          tooltip: getMetricTooltip('memoryPct'),
        },
        {
          label: `${es.analytics.coverage.capabilityDiscovery} %`,
          value: `${coverage.capability_discovery_pct.toFixed(1)}%`,
          tooltip: getMetricTooltip('capabilityDiscoveryPct'),
        },
        {
          label: `${es.analytics.coverage.guidedFallback} %`,
          value: `${coverage.guided_fallback_pct.toFixed(1)}%`,
          tooltip: getMetricTooltip('guidedFallbackPct'),
        },
        {
          label: `${es.analytics.coverage.legacy} %`,
          value: `${coverage.legacy_chat_pct.toFixed(1)}%`,
          tooltip: getMetricTooltip('legacyPct'),
        },
      ]
    : []

  return (
    <section>
      <h2 className="text-lg font-semibold text-foreground">{es.analytics.coverage.title}</h2>
      <p className="mt-1 text-[13px] text-muted">{es.analytics.coverage.subtitle}</p>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {isLoading && !coverage
          ? Array.from({ length: 6 }).map((_, index) => (
              <div
                key={index}
                className="animate-pulse rounded-2xl border border-border-subtle bg-surface-elevated px-4 py-5"
              >
                <div className="h-3 w-24 rounded bg-surface-subtle" />
                <div className="mt-4 h-8 w-16 rounded bg-surface-subtle" />
              </div>
            ))
          : cards.map((card) => <AnalyticsCard key={card.label} {...card} />)}
      </div>
    </section>
  )
}
