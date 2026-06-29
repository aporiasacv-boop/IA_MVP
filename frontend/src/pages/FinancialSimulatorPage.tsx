import { useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { AiActionButton } from '../components/executive/AiActionButton'
import { EnterpriseShell } from '../components/executive/EnterpriseShell'
import { buildFinancialQuestion } from '../enterpriseExperience/questions'
import { enterpriseExperienceStore } from '../enterpriseExperience/store'
import { useEnterpriseExperience } from '../enterpriseExperience'
import { useFinOps } from '../hooks/useFinOps'
import { es } from '../i18n/spanish'
import type { FinancialMetricKey } from '../enterpriseExperience/questions'

const SCENARIO_OPTIONS = [
  { id: 'piloto', label: 'Piloto' },
  { id: 'produccion', label: 'Producción' },
  { id: 'expansion', label: 'Expansión' },
] as const

export function FinancialSimulatorPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const { context, syncFromSearchParams, navigateToScreen } = useEnterpriseExperience()
  const { overview, providers, forecast, isLoading, error, refresh } = useFinOps()

  useEffect(() => {
    syncFromSearchParams(searchParams)
  }, [searchParams, syncFromSearchParams])

  const setScenario = (scenario: string) => {
    enterpriseExperienceStore.setContext({ scenario })
    setSearchParams({ scenario })
  }

  return (
    <EnterpriseShell
      screen="financial_simulator"
      title={es.executive.financial.title}
      subtitle={es.executive.financial.subtitle}
    >
      <div className="mx-auto max-w-6xl px-4 py-8 md:px-8 md:py-10">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap gap-2">
            {SCENARIO_OPTIONS.map((option) => (
              <button
                key={option.id}
                type="button"
                onClick={() => setScenario(option.id)}
                className={[
                  'rounded-full px-3 py-1.5 text-[12px] font-medium transition-premium',
                  context.scenario === option.id
                    ? 'bg-olnatura-600 text-white'
                    : 'border border-border-subtle bg-surface-elevated text-muted hover:text-foreground',
                ].join(' ')}
              >
                {option.label}
              </button>
            ))}
          </div>
          <button
            type="button"
            onClick={() => void refresh()}
            disabled={isLoading}
            className="executive-secondary-btn"
          >
            {isLoading ? es.common.loading : es.common.refresh}
          </button>
        </div>

        {error && (
          <div className="mt-6 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
            {error}
          </div>
        )}

        <section className="mt-10">
          <h2 className="text-[13px] font-semibold uppercase tracking-[0.14em] text-muted-light">
            {es.executive.financial.investmentOverview}
          </h2>
          <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <FinancialMetricCard
              label={es.executive.financial.monthlyCost}
              value={overview ? `$${overview.cost_month_usd.toFixed(2)}` : es.executive.financial.comingSoon}
              metricKey="monthly_cost"
              scenario={context.scenario}
              isLoading={isLoading}
            />
            <FinancialMetricCard
              label={es.executive.financial.annualCost}
              value={
                overview
                  ? `$${overview.cost_year_projected_usd.toFixed(2)}`
                  : es.executive.financial.comingSoon
              }
              metricKey="annual_cost"
              scenario={context.scenario}
              isLoading={isLoading}
            />
            <FinancialMetricCard
              label={es.executive.financial.roi}
              value={es.executive.financial.comingSoon}
              metricKey="roi"
              scenario={context.scenario}
              placeholder
              isLoading={isLoading}
            />
            <FinancialMetricCard
              label={es.executive.financial.llmSavings}
              value={
                overview
                  ? `${(overview.llm_avoidance_rate * 100).toFixed(1)}%`
                  : es.executive.financial.comingSoon
              }
              metricKey="llm_savings"
              scenario={context.scenario}
              isLoading={isLoading}
            />
          </div>
        </section>

        <section className="mt-12 grid gap-6 lg:grid-cols-2">
          <div className="rounded-2xl border border-border-subtle bg-surface-elevated p-6 shadow-[var(--shadow-soft)]">
            <div className="flex items-start justify-between gap-3">
              <h2 className="text-[13px] font-semibold uppercase tracking-[0.14em] text-muted-light">
                {es.executive.financial.usageModel}
              </h2>
              <AiActionButton
                question={buildFinancialQuestion('cost_per_user', context.scenario)}
                intent="explain"
                compact
              />
            </div>
            <dl className="mt-5 space-y-4">
              <FinancialRow label={es.executive.financial.users} value={es.executive.financial.comingSoon} />
              <FinancialRow label={es.executive.financial.queries} value={es.executive.financial.comingSoon} />
              <FinancialRow
                label={es.executive.financial.costPerUser}
                value={
                  overview
                    ? `$${overview.avg_cost_per_user_usd.toFixed(4)}`
                    : es.executive.financial.comingSoon
                }
              />
              <FinancialRow
                label={es.executive.financial.costPerSession}
                value={
                  overview
                    ? `$${overview.avg_cost_per_session_usd.toFixed(4)}`
                    : es.executive.financial.comingSoon
                }
              />
            </dl>
          </div>

          <div className="rounded-2xl border border-border-subtle bg-surface-elevated p-6 shadow-[var(--shadow-soft)]">
            <div className="flex items-start justify-between gap-3">
              <h2 className="text-[13px] font-semibold uppercase tracking-[0.14em] text-muted-light">
                {es.executive.financial.infrastructure}
              </h2>
              <AiActionButton
                question={buildFinancialQuestion('infrastructure', context.scenario)}
                intent="explain"
                compact
              />
            </div>
            <dl className="mt-5 space-y-4">
              <FinancialRow label="CPU" value={es.executive.financial.comingSoon} />
              <FinancialRow label="RAM" value={es.executive.financial.comingSoon} />
              <FinancialRow label="GPU" value={es.executive.financial.comingSoon} />
              <FinancialRow
                label={es.executive.financial.providers}
                value={
                  providers.length > 0
                    ? providers.map((p) => p.provider).join(', ')
                    : es.executive.financial.comingSoon
                }
              />
            </dl>
          </div>
        </section>

        <section className="mt-12">
          <h2 className="text-[13px] font-semibold uppercase tracking-[0.14em] text-muted-light">
            {es.executive.financial.scenarios}
          </h2>
          <p className="mt-2 text-[14px] text-muted">{es.executive.financial.scenariosHint}</p>
          <div className="mt-5 grid gap-4 md:grid-cols-3">
            {(forecast?.scenarios ?? PLACEHOLDER_SCENARIOS).map((scenario) => (
              <article
                key={scenario.users}
                className="rounded-2xl border border-border-subtle bg-surface-elevated/90 p-5"
              >
                <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-olnatura-600">
                  {scenario.users.toLocaleString('es-MX')} {es.executive.financial.users}
                </p>
                <p className="mt-3 text-[13px] text-muted">
                  {scenario.estimated_queries?.toLocaleString('es-MX') ?? '—'}{' '}
                  {es.executive.financial.queries}
                </p>
                <div className="mt-4 space-y-1.5 text-[12px] tabular-nums text-foreground/80">
                  <p>OpenAI · {formatCost(scenario.cost_openai_usd)}</p>
                  <p>Claude · {formatCost(scenario.cost_claude_usd)}</p>
                  <p>Ollama · {formatCost(scenario.cost_ollama_usd)}</p>
                </div>
                <div className="mt-4 border-t border-border-subtle pt-3">
                  <AiActionButton
                    question={buildFinancialQuestion('scenario', context.scenario)}
                    intent="explain"
                    compact
                  />
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="mt-12 rounded-2xl border border-dashed border-olnatura-200/60 bg-olnatura-50/40 px-6 py-8 text-center">
          <p className="text-[14px] font-medium text-olnatura-700">{es.executive.financial.roadmapTitle}</p>
          <p className="mx-auto mt-2 max-w-lg text-[13px] leading-6 text-muted">
            {es.executive.financial.roadmapHint}
          </p>
          <div className="mt-5 flex flex-wrap justify-center gap-2">
            <AiActionButton
              question={buildFinancialQuestion('monthly_cost', context.scenario)}
              intent="explain"
            />
            <button
              type="button"
              onClick={() => navigateToScreen('enterprise_ai')}
              className="executive-secondary-btn"
            >
              {es.experience.openEnterpriseAi}
            </button>
          </div>
        </section>
      </div>
    </EnterpriseShell>
  )
}

const PLACEHOLDER_SCENARIOS = [
  { users: 50, estimated_queries: 6000, cost_openai_usd: 0, cost_claude_usd: 0, cost_ollama_usd: 0 },
  { users: 200, estimated_queries: 24000, cost_openai_usd: 0, cost_claude_usd: 0, cost_ollama_usd: 0 },
  { users: 500, estimated_queries: 60000, cost_openai_usd: 0, cost_claude_usd: 0, cost_ollama_usd: 0 },
]

function formatCost(value: number | undefined): string {
  if (value == null || value === 0) return '—'
  return `$${value.toFixed(2)}`
}

function FinancialMetricCard({
  label,
  value,
  metricKey,
  scenario,
  placeholder = false,
  isLoading = false,
}: {
  label: string
  value: string
  metricKey: FinancialMetricKey
  scenario: string | null
  placeholder?: boolean
  isLoading?: boolean
}) {
  if (isLoading) {
    return (
      <div className="animate-pulse rounded-2xl border border-border-subtle bg-surface-elevated p-5">
        <div className="h-3 w-20 rounded bg-surface-subtle" />
        <div className="mt-4 h-8 w-24 rounded bg-surface-subtle" />
      </div>
    )
  }

  return (
    <div className="flex flex-col justify-between rounded-2xl border border-border-subtle bg-surface-elevated p-5 shadow-[var(--shadow-soft)]">
      <div>
        <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-light">{label}</p>
        <p
          className={[
            'mt-3 text-[1.65rem] font-semibold tabular-nums tracking-[-0.02em]',
            placeholder ? 'text-muted' : 'text-foreground',
          ].join(' ')}
        >
          {value}
        </p>
      </div>
      <div className="mt-4 border-t border-border-subtle pt-3">
        <AiActionButton
          question={buildFinancialQuestion(metricKey, scenario)}
          intent="explain"
          compact
        />
      </div>
    </div>
  )
}

function FinancialRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4 border-b border-border-subtle pb-3 last:border-0 last:pb-0">
      <dt className="text-[13px] text-muted">{label}</dt>
      <dd className="text-[13px] font-medium tabular-nums text-foreground">{value}</dd>
    </div>
  )
}
