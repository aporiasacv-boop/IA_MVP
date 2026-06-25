import { CoverageDashboard } from '../components/analytics/CoverageDashboard'
import { FinancialDashboard } from '../components/analytics/FinancialDashboard'
import { PerformanceDashboard } from '../components/analytics/PerformanceDashboard'
import { TopQueriesDashboard } from '../components/analytics/TopQueriesDashboard'
import { useBusinessAnalytics } from '../hooks/useBusinessAnalytics'
import { es } from '../i18n/spanish'

export function AnalyticsPage() {
  const { data, isLoading, error, refresh } = useBusinessAnalytics()

  return (
    <div className="h-full overflow-y-auto px-4 py-8 md:px-8 md:py-10">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-muted-light">
            {es.analytics.eyebrow}
          </p>
          <h1 className="mt-3 text-2xl font-semibold tracking-[-0.03em] text-foreground">
            {es.analytics.title}
          </h1>
          <p className="mt-2 max-w-2xl text-[13px] text-muted">{es.analytics.subtitle}</p>
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
          {es.common.errorAnalytics}
        </div>
      )}

      <div className="mt-10 space-y-12">
        <CoverageDashboard coverage={data?.coverage ?? null} isLoading={isLoading} />
        <PerformanceDashboard performance={data?.performance ?? null} isLoading={isLoading} />
        <FinancialDashboard financial={data?.financial ?? null} isLoading={isLoading} />
        <TopQueriesDashboard topQueries={data?.topQueries ?? []} isLoading={isLoading} />
      </div>
    </div>
  )
}
