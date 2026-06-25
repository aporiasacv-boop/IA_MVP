import { useFinOps } from '../hooks/useFinOps'
import { es } from '../i18n/spanish'

export function FinOpsPage() {
  const { overview, providers, savings, forecast, isLoading, error, refresh } = useFinOps()

  return (
    <div className="h-full overflow-y-auto px-4 py-8 md:px-8 md:py-10">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-muted-light">
            {es.finops.eyebrow}
          </p>
          <h1 className="mt-3 text-2xl font-semibold tracking-[-0.03em]">{es.finops.title}</h1>
          <p className="mt-2 max-w-2xl text-[13px] text-muted">{es.finops.subtitle}</p>
        </div>
        <button
          type="button"
          onClick={() => void refresh()}
          disabled={isLoading}
          className="rounded-lg border border-border-subtle bg-surface-elevated px-3 py-2 text-[12px] font-medium text-muted hover:text-foreground disabled:opacity-50"
        >
          {isLoading ? es.common.loading : es.common.refresh}
        </button>
      </div>

      {error && (
        <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          {error}
        </div>
      )}

      <section className="mt-8">
        <h2 className="text-[13px] font-semibold uppercase tracking-[0.14em] text-muted-light">
          {es.finops.executiveSummary}
        </h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard label={es.finops.costToday} value={`$${overview?.cost_today_usd?.toFixed(4) ?? '—'}`} />
          <StatCard label={es.finops.costMonth} value={`$${overview?.cost_month_usd?.toFixed(4) ?? '—'}`} />
          <StatCard
            label={es.finops.costYearProjected}
            value={`$${overview?.cost_year_projected_usd?.toFixed(2) ?? '—'}`}
          />
          <StatCard
            label={es.finops.llmAvoidance}
            value={
              overview ? `${(overview.llm_avoidance_rate * 100).toFixed(1)}%` : '—'
            }
          />
        </div>
      </section>

      <section className="mt-10">
        <h2 className="text-[13px] font-semibold uppercase tracking-[0.14em] text-muted-light">
          {es.finops.costBreakdown}
        </h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard label={es.finops.costPerUser} value={`$${overview?.avg_cost_per_user_usd?.toFixed(6) ?? '—'}`} />
          <StatCard label={es.finops.costPerSession} value={`$${overview?.avg_cost_per_session_usd?.toFixed(6) ?? '—'}`} />
          <StatCard label={es.finops.knowledgeRuntime} value={savings ? `${(savings.knowledge_avoidance_rate * 100).toFixed(1)}%` : '—'} />
          <StatCard label={es.finops.businessPipeline} value={savings ? `${(savings.pipeline_avoidance_rate * 100).toFixed(1)}%` : '—'} />
        </div>
      </section>

      <section className="mt-10">
        <h2 className="text-[13px] font-semibold uppercase tracking-[0.14em] text-muted-light">
          {es.finops.providerComparison}
        </h2>
        <div className="mt-4 overflow-x-auto rounded-xl border border-border-subtle">
          <table className="min-w-full text-left text-[13px]">
            <thead className="bg-surface-elevated/80 text-[11px] uppercase tracking-[0.12em] text-muted-light">
              <tr>
                <th className="px-4 py-3">{es.finops.table.provider}</th>
                <th className="px-4 py-3">{es.finops.table.usage}</th>
                <th className="px-4 py-3">{es.finops.table.cost}</th>
                <th className="px-4 py-3">{es.finops.table.tokens}</th>
                <th className="px-4 py-3">{es.finops.table.latency}</th>
                <th className="px-4 py-3">{es.finops.table.share}</th>
              </tr>
            </thead>
            <tbody>
              {providers.map((provider) => (
                <tr key={provider.provider} className="border-t border-border-subtle">
                  <td className="px-4 py-3 font-medium capitalize">{provider.provider}</td>
                  <td className="px-4 py-3 tabular-nums">{provider.requests}</td>
                  <td className="px-4 py-3 tabular-nums">${provider.cost_usd.toFixed(6)}</td>
                  <td className="px-4 py-3 tabular-nums">{provider.total_tokens}</td>
                  <td className="px-4 py-3 tabular-nums">{provider.average_latency_ms.toFixed(1)} ms</td>
                  <td className="px-4 py-3 tabular-nums">{provider.participation_pct.toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="mt-10">
        <h2 className="text-[13px] font-semibold uppercase tracking-[0.14em] text-muted-light">
          {es.finops.savingsTitle}
        </h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <StatCard
            label={es.finops.avoidedCost}
            value={`$${savings?.total_avoided_cost_usd?.toFixed(4) ?? '—'}`}
          />
          <StatCard
            label={es.finops.accumulatedSavings}
            value={`$${savings?.accumulated_savings_usd?.toFixed(4) ?? '—'}`}
          />
        </div>
        <ul className="mt-4 space-y-2">
          {(savings?.by_route ?? []).slice(0, 8).map((route) => (
            <li
              key={route.handled_by}
              className="flex items-center justify-between rounded-lg border border-border-subtle bg-surface-elevated/60 px-4 py-3 text-[13px]"
            >
              <span>{route.handled_by}</span>
              <span className="tabular-nums text-muted">
                {route.queries} · ${route.avoided_cost_usd.toFixed(4)}
              </span>
            </li>
          ))}
        </ul>
      </section>

      <section className="mt-10">
        <h2 className="text-[13px] font-semibold uppercase tracking-[0.14em] text-muted-light">
          {es.finops.forecastTitle}
        </h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {(forecast?.scenarios ?? []).map((scenario) => (
            <article
              key={scenario.users}
              className="rounded-xl border border-border-subtle bg-surface-elevated/70 px-4 py-4"
            >
              <p className="text-[11px] uppercase tracking-[0.12em] text-muted-light">
                {scenario.users.toLocaleString('es-MX')} {es.finops.users}
              </p>
              <p className="mt-2 text-[13px] text-muted">
                {scenario.estimated_queries.toLocaleString('es-MX')} {es.finops.queries}
              </p>
              <div className="mt-3 space-y-1 text-[12px]">
                <p>OpenAI: ${scenario.cost_openai_usd.toFixed(2)}</p>
                <p>Claude: ${scenario.cost_claude_usd.toFixed(2)}</p>
                <p>Ollama: ${scenario.cost_ollama_usd.toFixed(2)}</p>
              </div>
              <p className="mt-3 text-[12px] text-muted">
                CPU {scenario.estimated_cpu_cores} · RAM {scenario.estimated_ram_gb} GB · GPU{' '}
                {scenario.estimated_gpu_gb} GB
              </p>
            </article>
          ))}
        </div>
      </section>
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border-subtle bg-surface-elevated/70 px-4 py-4">
      <p className="text-[11px] uppercase tracking-[0.12em] text-muted-light">{label}</p>
      <p className="mt-2 text-2xl font-semibold tabular-nums">{value}</p>
    </div>
  )
}
