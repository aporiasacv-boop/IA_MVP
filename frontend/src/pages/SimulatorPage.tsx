import { useSimulator } from '../hooks/useSimulator'
import { es } from '../i18n/spanish'

export function SimulatorPage() {
  const {
    predefined,
    scenario,
    setScenario,
    result,
    recommendations,
    baselineSource,
    isLoading,
    error,
    run,
    applyPredefined,
  } = useSimulator()

  const update = <K extends keyof typeof scenario>(key: K, value: (typeof scenario)[K]) => {
    setScenario({ ...scenario, [key]: value })
  }

  return (
    <div className="h-full overflow-y-auto px-4 py-8 md:px-8 md:py-10">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-muted-light">
            {es.simulator.eyebrow}
          </p>
          <h1 className="mt-3 text-2xl font-semibold tracking-[-0.03em]">{es.simulator.title}</h1>
          <p className="mt-2 max-w-2xl text-[13px] text-muted">{es.simulator.subtitle}</p>
          <p className="mt-1 text-[12px] text-muted-light">
            {es.simulator.baseline}: {baselineSource}
          </p>
        </div>
        <button
          type="button"
          onClick={() => void run()}
          disabled={isLoading}
          className="rounded-lg border border-border-subtle bg-surface-elevated px-3 py-2 text-[12px] font-medium text-muted hover:text-foreground disabled:opacity-50"
        >
          {isLoading ? es.common.loading : es.simulator.run}
        </button>
      </div>

      {error && (
        <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          {error}
        </div>
      )}

      <section className="mt-8">
        <h2 className="text-[13px] font-semibold uppercase tracking-[0.14em] text-muted-light">
          {es.simulator.predefined}
        </h2>
        <div className="mt-4 flex flex-wrap gap-2">
          {predefined.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => applyPredefined(item.id)}
              className="rounded-lg border border-border-subtle bg-surface-elevated px-3 py-2 text-[12px] hover:bg-surface-subtle"
            >
              {item.name}
            </button>
          ))}
        </div>
      </section>

      <section className="mt-10 grid gap-6 xl:grid-cols-2">
        <div className="rounded-xl border border-border-subtle bg-surface-elevated/70 p-4">
          <h2 className="text-[13px] font-semibold uppercase tracking-[0.14em] text-muted-light">
            {es.simulator.parameters}
          </h2>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <Field label={es.simulator.users} value={scenario.users} onChange={(v) => update('users', Number(v))} />
            <Field
              label={es.simulator.queriesPerUser}
              value={scenario.queries_per_user_day}
              onChange={(v) => update('queries_per_user_day', Number(v))}
            />
            <Field
              label={es.simulator.pipelinePct}
              value={scenario.business_pipeline_pct ?? 0}
              onChange={(v) => update('business_pipeline_pct', Number(v))}
            />
            <Field
              label={es.simulator.knowledgePct}
              value={scenario.knowledge_service_pct ?? 0}
              onChange={(v) => update('knowledge_service_pct', Number(v))}
            />
            <Field
              label={es.simulator.memoryPct}
              value={scenario.conversation_memory_pct ?? 0}
              onChange={(v) => update('conversation_memory_pct', Number(v))}
            />
            <Field
              label={es.simulator.executivePct}
              value={scenario.executive_reasoning_pct ?? 0}
              onChange={(v) => update('executive_reasoning_pct', Number(v))}
            />
            <Field
              label={es.simulator.legacyPct}
              value={scenario.legacy_chat_pct ?? 0}
              onChange={(v) => update('legacy_chat_pct', Number(v))}
            />
            <Field
              label={es.simulator.provider}
              value={scenario.llm_provider}
              onChange={(v) => update('llm_provider', v)}
            />
            <Field
              label={es.simulator.concurrency}
              value={scenario.concurrency}
              onChange={(v) => update('concurrency', Number(v))}
            />
            <Field
              label={es.simulator.peakHours}
              value={scenario.peak_hours}
              onChange={(v) => update('peak_hours', Number(v))}
            />
            <Field
              label={es.simulator.workingDays}
              value={scenario.working_days}
              onChange={(v) => update('working_days', Number(v))}
            />
          </div>
        </div>

        <div className="space-y-6">
          <Panel title={es.simulator.executiveSummary}>
            <Metric label={es.simulator.monthlyCost} value={`$${result?.metrics.cost_usd.toFixed(2) ?? '—'}`} />
            <Metric
              label={es.simulator.yearlyCost}
              value={`$${((result?.metrics.cost_usd ?? 0) * 12).toFixed(2)}`}
            />
            <Metric label={es.simulator.avoidedCost} value={`$${result?.metrics.avoided_cost_usd.toFixed(2) ?? '—'}`} />
            <Metric label={es.simulator.roi} value={`${result?.metrics.roi_pct.toFixed(1) ?? '—'}%`} />
          </Panel>
          <Panel title={es.simulator.infrastructure}>
            <Metric label="CPU" value={`${result?.metrics.estimated_cpu_cores ?? '—'} núcleos`} />
            <Metric label="RAM" value={`${result?.metrics.estimated_ram_gb ?? '—'} GB`} />
            <Metric label="GPU" value={`${result?.metrics.estimated_gpu_gb ?? '—'} GB`} />
            <Metric label={es.simulator.latencyP95} value={`${result?.metrics.latency_p95_ms ?? '—'} ms`} />
          </Panel>
        </div>
      </section>

      {result && (
        <section className="mt-10">
          <h2 className="text-[13px] font-semibold uppercase tracking-[0.14em] text-muted-light">
            {es.simulator.providerComparison}
          </h2>
          <div className="mt-4 overflow-x-auto rounded-xl border border-border-subtle">
            <table className="min-w-full text-left text-[13px]">
              <thead className="bg-surface-elevated/80 text-[11px] uppercase tracking-[0.12em] text-muted-light">
                <tr>
                  <th className="px-4 py-3">{es.finops.table.provider}</th>
                  <th className="px-4 py-3">{es.finops.table.cost}</th>
                  <th className="px-4 py-3">{es.finops.table.latency}</th>
                  <th className="px-4 py-3">ROI</th>
                  <th className="px-4 py-3">{es.finops.table.share}</th>
                </tr>
              </thead>
              <tbody>
                {result.provider_comparison.map((provider) => (
                  <tr key={provider.provider} className="border-t border-border-subtle">
                    <td className="px-4 py-3 capitalize">{provider.provider}</td>
                    <td className="px-4 py-3">${provider.cost_usd.toFixed(4)}</td>
                    <td className="px-4 py-3">{provider.avg_latency_ms.toFixed(1)} ms</td>
                    <td className="px-4 py-3">{provider.roi_pct.toFixed(1)}%</td>
                    <td className="px-4 py-3">{provider.participation_pct.toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {recommendations.length > 0 && (
        <section className="mt-10">
          <h2 className="text-[13px] font-semibold uppercase tracking-[0.14em] text-muted-light">
            {es.simulator.recommendations}
          </h2>
          <ul className="mt-4 space-y-3">
            {recommendations.map((item) => (
              <li key={item.title} className="rounded-xl border border-border-subtle bg-surface-elevated/70 p-4">
                <p className="text-[11px] uppercase tracking-[0.12em] text-muted-light">{item.category}</p>
                <h3 className="mt-1 text-[15px] font-medium">{item.title}</h3>
                <p className="mt-2 text-[13px] text-muted">{item.detail}</p>
                <p className="mt-2 text-[12px] tabular-nums text-olnatura-700">{item.metric_value}</p>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  )
}

function Field({
  label,
  value,
  onChange,
}: {
  label: string
  value: string | number
  onChange: (value: string) => void
}) {
  return (
    <label className="block text-[12px]">
      <span className="text-muted-light">{label}</span>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 w-full rounded-lg border border-border-subtle bg-surface px-2 py-1.5 text-[13px]"
      />
    </label>
  )
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-border-subtle bg-surface-elevated/70 p-4">
      <h2 className="text-[13px] font-semibold uppercase tracking-[0.14em] text-muted-light">{title}</h2>
      <div className="mt-4 grid gap-3 sm:grid-cols-2">{children}</div>
    </div>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-[11px] uppercase tracking-[0.12em] text-muted-light">{label}</p>
      <p className="mt-1 text-lg font-semibold tabular-nums">{value}</p>
    </div>
  )
}
