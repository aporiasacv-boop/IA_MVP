import type { ProviderCostItem } from '../../types/aiCosts'
import { es } from '../../i18n/spanish'
import { AnalyticsCard } from '../analytics/AnalyticsCard'

const currency = new Intl.NumberFormat('es-MX', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 6,
})

interface ProviderComparisonTableProps {
  providers: ProviderCostItem[]
}

export function ProviderComparisonTable({ providers }: ProviderComparisonTableProps) {
  if (!providers.length) {
    return <p className="text-[13px] text-muted">{es.aiCosts.noProviderData}</p>
  }
  return (
    <div className="overflow-x-auto rounded-2xl border border-border-subtle">
      <table className="min-w-full text-left text-[12px]">
        <thead className="bg-surface-subtle text-muted">
          <tr>
            <th className="px-4 py-3 font-medium">{es.aiCosts.provider}</th>
            <th className="px-4 py-3 font-medium">{es.aiCosts.requests}</th>
            <th className="px-4 py-3 font-medium">{es.aiCosts.tokens}</th>
            <th className="px-4 py-3 font-medium">{es.aiCosts.cost}</th>
            <th className="px-4 py-3 font-medium">{es.aiCosts.latency}</th>
          </tr>
        </thead>
        <tbody>
          {providers.map((item) => (
            <tr key={item.provider} className="border-t border-border-subtle">
              <td className="px-4 py-3 font-medium text-foreground">{item.provider}</td>
              <td className="px-4 py-3 text-muted">{item.requests}</td>
              <td className="px-4 py-3 text-muted">
                {item.tokens_input + item.tokens_output}
              </td>
              <td className="px-4 py-3 text-muted">{currency.format(item.estimated_cost)}</td>
              <td className="px-4 py-3 text-muted">{item.average_latency.toFixed(3)}s</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

interface AICostPanelsProps {
  summary: {
    llm_requests: number
    tokens_input: number
    tokens_output: number
    estimated_cost: number
    average_latency: number
    average_cost_per_question: number
    daily_cost: number
    monthly_cost: number
    cost_per_query: number
    hallucination_guard_triggered: number
    llm_fallbacks: number
    provider_comparison: ProviderCostItem[]
    cost_per_user: Record<string, number>
  } | null
  isLoading?: boolean
}

export function AICostPanels({ summary, isLoading = false }: AICostPanelsProps) {
  const cards = summary
    ? [
        { label: es.aiCosts.totalRequests, value: String(summary.llm_requests) },
        { label: es.aiCosts.dailyCost, value: currency.format(summary.daily_cost) },
        { label: es.aiCosts.monthlyCost, value: currency.format(summary.monthly_cost) },
        { label: es.aiCosts.costPerQuery, value: currency.format(summary.cost_per_query) },
        { label: es.aiCosts.avgCostPerQuestion, value: currency.format(summary.average_cost_per_question) },
        { label: es.aiCosts.totalTokens, value: String(summary.tokens_input + summary.tokens_output) },
        { label: es.aiCosts.avgLatency, value: `${summary.average_latency.toFixed(3)}s` },
        { label: es.aiCosts.hallucinationGuard, value: String(summary.hallucination_guard_triggered) },
      ]
    : []

  return (
    <div className="space-y-10">
      <section>
        <h2 className="text-lg font-semibold text-foreground">{es.aiCosts.overview}</h2>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {isLoading && !summary
            ? Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="animate-pulse rounded-2xl border border-border-subtle bg-surface-elevated px-4 py-5">
                  <div className="h-3 w-24 rounded bg-surface-subtle" />
                  <div className="mt-4 h-8 w-16 rounded bg-surface-subtle" />
                </div>
              ))
            : cards.map((card) => <AnalyticsCard key={card.label} label={card.label} value={card.value} />)}
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-foreground">{es.aiCosts.providerComparison}</h2>
        <div className="mt-4">
          <ProviderComparisonTable providers={summary?.provider_comparison ?? []} />
        </div>
      </section>

      {summary && Object.keys(summary.cost_per_user).length > 0 && (
        <section>
          <h2 className="text-lg font-semibold text-foreground">{es.aiCosts.costPerUser}</h2>
          <ul className="mt-4 space-y-2 text-[13px] text-muted">
            {Object.entries(summary.cost_per_user).map(([user, cost]) => (
              <li key={user}>
                {user}: {currency.format(cost)}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  )
}
