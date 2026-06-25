import type { ReactNode } from 'react'
import { useDecisionCenter } from '../hooks/useDecisionCenter'
import { es } from '../i18n/spanish'

export function DecisionCenterPage() {
  const {
    decisionTypes,
    decisionLabels,
    selectedType,
    setSelectedType,
    scenarioId,
    setScenarioId,
    packageData,
    isLoading,
    error,
    recommend,
  } = useDecisionCenter()

  return (
    <div className="h-full overflow-y-auto px-4 py-8 md:px-8 md:py-10">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-muted-light">
            {es.decisionCenter.eyebrow}
          </p>
          <h1 className="mt-3 text-2xl font-semibold tracking-[-0.03em]">{es.decisionCenter.title}</h1>
          <p className="mt-2 max-w-2xl text-[13px] text-muted">{es.decisionCenter.subtitle}</p>
        </div>
        <button
          type="button"
          onClick={() => void recommend()}
          disabled={isLoading}
          className="rounded-lg border border-border-subtle bg-surface-elevated px-3 py-2 text-[12px] font-medium text-muted hover:text-foreground disabled:opacity-50"
        >
          {isLoading ? es.common.loading : es.decisionCenter.generate}
        </button>
      </div>

      {error && (
        <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          {error}
        </div>
      )}

      <section className="mt-8 grid gap-4 md:grid-cols-2">
        <div>
          <label className="text-[12px] font-medium text-muted-light">{es.decisionCenter.decisionType}</label>
          <select
            value={selectedType}
            onChange={(event) => setSelectedType(event.target.value as typeof selectedType)}
            className="mt-2 w-full rounded-lg border border-border-subtle bg-surface-elevated px-3 py-2 text-[13px]"
          >
            {decisionTypes.map((type) => (
              <option key={type} value={type}>
                {decisionLabels[type] ?? type}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-[12px] font-medium text-muted-light">{es.decisionCenter.scenario}</label>
          <select
            value={scenarioId}
            onChange={(event) => setScenarioId(event.target.value)}
            className="mt-2 w-full rounded-lg border border-border-subtle bg-surface-elevated px-3 py-2 text-[13px]"
          >
            {es.decisionCenter.scenarios.map((item) => (
              <option key={item.id} value={item.id}>
                {item.label}
              </option>
            ))}
          </select>
        </div>
      </section>

      {packageData && (
        <div className="mt-10 space-y-8">
          <Panel title={es.decisionCenter.executiveSummary}>
            <p className="text-[13px] leading-relaxed text-muted">{packageData.executive_summary}</p>
          </Panel>

          <div className="grid gap-6 xl:grid-cols-2">
            <Panel title={es.decisionCenter.mainRecommendation}>
              <RecommendationCard item={packageData.main_recommendation} />
              <p className="mt-3 text-[12px] text-muted-light">
                {es.decisionCenter.confidence}: {(packageData.confidence_level * 100).toFixed(1)}%
              </p>
            </Panel>

            <Panel title={es.decisionCenter.alternatives}>
              {packageData.alternative_recommendations.length === 0 ? (
                <p className="text-[13px] text-muted">{es.common.noData}</p>
              ) : (
                <ul className="space-y-3">
                  {packageData.alternative_recommendations.map((item) => (
                    <li key={item.title}>
                      <RecommendationCard item={item} compact />
                    </li>
                  ))}
                </ul>
              )}
            </Panel>
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            <Metric
              label={es.decisionCenter.economicImpact}
              value={`$${packageData.financial_impact.monthly_projection_usd.toFixed(4)} USD`}
            />
            <Metric
              label={es.decisionCenter.expectedSavings}
              value={`$${packageData.financial_impact.avoided_cost_usd.toFixed(4)} USD`}
            />
            <Metric
              label={es.decisionCenter.confidence}
              value={`${(packageData.confidence_level * 100).toFixed(1)}%`}
            />
          </div>

          <div className="grid gap-6 xl:grid-cols-2">
            <ListPanel title={es.decisionCenter.risks} items={packageData.risks} tone="risk" />
            <ListPanel title={es.decisionCenter.opportunities} items={packageData.opportunities} tone="opportunity" />
          </div>

          <Panel title={es.decisionCenter.evidence}>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-[12px]">
                <thead>
                  <tr className="border-b border-border-subtle text-muted-light">
                    <th className="py-2 pr-3">{es.decisionCenter.source}</th>
                    <th className="py-2 pr-3">{es.decisionCenter.metric}</th>
                    <th className="py-2 pr-3">{es.common.count}</th>
                    <th className="py-2">{es.decisionCenter.confidence}</th>
                  </tr>
                </thead>
                <tbody>
                  {packageData.evidence_used.map((item) => (
                    <tr key={item.evidence_id} className="border-b border-border-subtle/60">
                      <td className="py-2 pr-3">{item.source}</td>
                      <td className="py-2 pr-3">{item.metric}</td>
                      <td className="py-2 pr-3">{item.value}</td>
                      <td className="py-2">{(item.confidence * 100).toFixed(0)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Panel>

          {packageData.limitations.length > 0 && (
            <Panel title={es.decisionCenter.limitations}>
              <ul className="list-disc space-y-1 pl-5 text-[13px] text-muted">
                {packageData.limitations.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </Panel>
          )}
        </div>
      )}
    </div>
  )
}

function Panel({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="rounded-xl border border-border-subtle bg-surface-elevated/70 p-4">
      <h2 className="text-[13px] font-semibold uppercase tracking-[0.14em] text-muted-light">{title}</h2>
      <div className="mt-4">{children}</div>
    </section>
  )
}

function RecommendationCard({
  item,
  compact = false,
}: {
  item: { title: string; detail: string; confidence: number }
  compact?: boolean
}) {
  return (
    <div className={compact ? 'rounded-lg border border-border-subtle/80 bg-surface-subtle/50 p-3' : ''}>
      <p className="text-[14px] font-medium">{item.title}</p>
      <p className="mt-1 text-[13px] text-muted">{item.detail}</p>
      {!compact && (
        <p className="mt-2 text-[12px] text-muted-light">
          Confianza local: {(item.confidence * 100).toFixed(0)}%
        </p>
      )}
    </div>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border-subtle bg-surface-elevated/70 p-4">
      <p className="text-[11px] uppercase tracking-[0.14em] text-muted-light">{label}</p>
      <p className="mt-2 text-xl font-semibold">{value}</p>
    </div>
  )
}

function ListPanel({
  title,
  items,
  tone,
}: {
  title: string
  items: string[]
  tone: 'risk' | 'opportunity'
}) {
  const color = tone === 'risk' ? 'text-amber-800' : 'text-emerald-800'
  return (
    <Panel title={title}>
      {items.length === 0 ? (
        <p className="text-[13px] text-muted">{es.common.noData}</p>
      ) : (
        <ul className={`list-disc space-y-1 pl-5 text-[13px] ${color}`}>
          {items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      )}
    </Panel>
  )
}
