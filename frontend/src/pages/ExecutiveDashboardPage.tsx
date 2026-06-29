import { useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { AiActionButton } from '../components/executive/AiActionButton'
import { ExecutiveAdvisorPanel } from '../components/executive/ExecutiveAdvisorPanel'
import { EnterpriseShell } from '../components/executive/EnterpriseShell'
import { ExecutiveKpiCard } from '../components/executive/ExecutiveKpiCard'
import { buildKpiQuestion } from '../enterpriseExperience/questions'
import { enterpriseExperienceStore } from '../enterpriseExperience/store'
import { useEnterpriseExperience } from '../enterpriseExperience'
import { useBusinessAnalytics } from '../hooks/useBusinessAnalytics'
import { useExecutiveAdvisor } from '../hooks/useExecutiveAdvisor'
import { es } from '../i18n/spanish'

const formatter = new Intl.NumberFormat('es-MX')
const PERIOD_OPTIONS = ['junio', 'julio', 'agosto'] as const

export function ExecutiveDashboardPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const { context, syncFromSearchParams, navigateToScreen } = useEnterpriseExperience()
  const { data, isLoading, error, refresh } = useBusinessAnalytics()
  const report = data?.report
  const financial = data?.financial
  const topQueries = data?.topQueries?.slice(0, 5) ?? []
  const advisor = useExecutiveAdvisor({
    period: context.period,
    scenario: context.scenario,
  })

  const handleAdvisorAnalyze = (question: string) => {
    navigateToScreen('enterprise_ai', { q: question })
  }

  useEffect(() => {
    syncFromSearchParams(searchParams)
  }, [searchParams, syncFromSearchParams])

  const successRate = report ? `${report.success_rate.toFixed(1)}%` : '—'
  const coverageScore = report ? `${report.coverage_score.toFixed(0)}%` : '—'
  const entitiesTotal = report?.business_entities_total
  const alerts = report?.average_alerts

  const setPeriod = (period: string) => {
    enterpriseExperienceStore.setContext({ period })
    setSearchParams({ period })
  }

  return (
    <EnterpriseShell
      screen="executive_dashboard"
      title={es.executive.dashboard.title}
      subtitle={es.executive.dashboard.subtitle}
    >
      <div className="mx-auto max-w-6xl px-4 py-8 md:px-8 md:py-10">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap gap-2">
            {PERIOD_OPTIONS.map((period) => (
              <button
                key={period}
                type="button"
                onClick={() => setPeriod(period)}
                className={[
                  'rounded-full px-3 py-1.5 text-[12px] font-medium capitalize transition-premium',
                  context.period === period
                    ? 'bg-olnatura-600 text-white'
                    : 'border border-border-subtle bg-surface-elevated text-muted hover:text-foreground',
                ].join(' ')}
              >
                {period}
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
            {es.executiveAdvisor.dailyAgenda}
          </h2>
          <div className="mt-5">
            <ExecutiveAdvisorPanel
              data={advisor.data}
              isLoading={advisor.isLoading}
              error={advisor.error}
              onAnalyze={handleAdvisorAnalyze}
              compact
            />
          </div>
        </section>

        <section className="mt-10">
          <h2 className="text-[13px] font-semibold uppercase tracking-[0.14em] text-muted-light">
            {es.executive.dashboard.keyIndicators}
          </h2>
          <div className="mt-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            <ExecutiveKpiCard
              label={es.executive.dashboard.clients}
              value={entitiesTotal != null ? formatter.format(entitiesTotal) : '—'}
              hint={es.executive.dashboard.clientsHint}
              kpiKey="clients"
              isLoading={isLoading}
            />
            <ExecutiveKpiCard
              label={es.executive.dashboard.activity}
              value={data ? formatter.format(data.coverage.total_requests) : '—'}
              hint={es.executive.dashboard.activityHint}
              kpiKey="activity"
              isLoading={isLoading}
            />
            <ExecutiveKpiCard
              label={es.executive.dashboard.operationalHealth}
              value={successRate}
              hint={`${es.executive.dashboard.coverage}: ${coverageScore}`}
              trend={report && report.success_rate >= 85 ? 'up' : 'neutral'}
              kpiKey="operational_health"
              isLoading={isLoading}
            />
            <ExecutiveKpiCard
              label={es.executive.dashboard.risks}
              value={report ? `${report.legacy_rate.toFixed(1)}%` : '—'}
              hint={es.executive.dashboard.risksHint}
              trend={report && report.legacy_rate > 15 ? 'down' : 'neutral'}
              kpiKey="risks"
              isLoading={isLoading}
            />
            <ExecutiveKpiCard
              label={es.executive.dashboard.alerts}
              value={alerts != null ? formatter.format(Math.round(alerts)) : '—'}
              hint={es.executive.dashboard.alertsHint}
              kpiKey="alerts"
              isLoading={isLoading}
            />
            <ExecutiveKpiCard
              label={es.executive.dashboard.efficiency}
              value={financial ? `${(financial.ai_avoidance_rate * 100).toFixed(1)}%` : '—'}
              hint={es.executive.dashboard.efficiencyHint}
              kpiKey="efficiency"
              isLoading={isLoading}
            />
          </div>
        </section>

        <section className="mt-12">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <h2 className="text-[13px] font-semibold uppercase tracking-[0.14em] text-muted-light">
                {es.executive.dashboard.recentFocus}
              </h2>
              <p className="mt-1 text-[14px] text-muted">{es.executive.dashboard.recentFocusHint}</p>
            </div>
            <AiActionButton question={buildKpiQuestion('operational_health', context.period)} />
          </div>
          <ul className="mt-5 space-y-3">
            {isLoading && topQueries.length === 0
              ? Array.from({ length: 4 }).map((_, i) => (
                  <li
                    key={i}
                    className="animate-pulse rounded-xl border border-border-subtle bg-surface-elevated px-4 py-4"
                  >
                    <div className="h-4 w-2/3 rounded bg-surface-subtle" />
                  </li>
                ))
              : topQueries.map((item) => (
                  <li
                    key={item.question}
                    className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-border-subtle bg-surface-elevated/80 px-4 py-4"
                  >
                    <div>
                      <p className="text-[14px] font-medium text-foreground">{item.question}</p>
                      <p className="mt-1 text-[12px] text-muted">
                        {formatter.format(item.count)} consultas ·{' '}
                        {(item.success_rate * 100).toFixed(0)}% éxito
                      </p>
                    </div>
                    <AiActionButton question={item.question} compact />
                  </li>
                ))}
            {!isLoading && topQueries.length === 0 && (
              <li className="rounded-xl border border-dashed border-border-subtle px-4 py-8 text-center">
                <p className="text-[13px] text-muted">{es.executive.dashboard.noActivityYet}</p>
                <div className="mt-4 flex justify-center gap-2">
                  <AiActionButton question={buildKpiQuestion('activity', context.period)} compact />
                  <button
                    type="button"
                    onClick={() => navigateToScreen('enterprise_ai')}
                    className="executive-secondary-btn"
                  >
                    {es.experience.openEnterpriseAi}
                  </button>
                </div>
              </li>
            )}
          </ul>
        </section>
      </div>
    </EnterpriseShell>
  )
}
