import type { FinancialAnalytics } from '../../types/businessAnalytics'
import { es, getMetricTooltip } from '../../i18n/spanish'
import { AnalyticsCard } from './AnalyticsCard'

const formatter = new Intl.NumberFormat('es-MX', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 4,
})

interface FinancialDashboardProps {
  financial: FinancialAnalytics | null
  isLoading?: boolean
}

export function FinancialDashboard({ financial, isLoading = false }: FinancialDashboardProps) {
  const pct = (value: number) => `${(value * 100).toFixed(1)}%`

  const cards = financial
    ? [
        {
          label: es.analytics.financial.aiAvoidanceRate,
          value: pct(financial.ai_avoidance_rate),
          tooltip: getMetricTooltip('aiAvoidanceRate'),
        },
        {
          label: es.analytics.financial.legacyDependencyRate,
          value: pct(financial.legacy_dependency_rate),
          tooltip: getMetricTooltip('legacyDependencyRate'),
        },
        {
          label: es.analytics.financial.gptCost,
          value: formatter.format(financial.estimated_gpt_cost),
          tooltip: getMetricTooltip('equivalentGptCost'),
        },
        {
          label: es.analytics.financial.claudeCost,
          value: formatter.format(financial.estimated_claude_cost),
          tooltip: getMetricTooltip('equivalentClaudeCost'),
        },
        {
          label: es.analytics.financial.ollamaCost,
          value: formatter.format(financial.estimated_ollama_cost),
          tooltip: getMetricTooltip('equivalentOllamaCost'),
        },
        {
          label: es.analytics.financial.deterministicRequests,
          value: formatter.format(financial.deterministic_requests),
        },
      ]
    : []

  return (
    <section>
      <h2 className="text-lg font-semibold text-foreground">{es.analytics.financial.title}</h2>
      <p className="mt-1 text-[13px] text-muted">{es.analytics.financial.subtitle}</p>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {isLoading && !financial
          ? Array.from({ length: 6 }).map((_, index) => (
              <div
                key={index}
                className="animate-pulse rounded-2xl border border-border-subtle bg-surface-elevated px-4 py-5"
              >
                <div className="h-3 w-28 rounded bg-surface-subtle" />
                <div className="mt-4 h-8 w-20 rounded bg-surface-subtle" />
              </div>
            ))
          : cards.map((card) => <AnalyticsCard key={card.label} {...card} />)}
      </div>
    </section>
  )
}
