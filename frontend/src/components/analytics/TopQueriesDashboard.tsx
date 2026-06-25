import type { TopQueryAnalyticsItem } from '../../types/businessAnalytics'
import { es, translateHandledBy } from '../../i18n/spanish'

const formatter = new Intl.NumberFormat('es-MX')

interface TopQueriesDashboardProps {
  topQueries: TopQueryAnalyticsItem[]
  isLoading?: boolean
}

export function TopQueriesDashboard({
  topQueries,
  isLoading = false,
}: TopQueriesDashboardProps) {
  return (
    <section>
      <h2 className="text-lg font-semibold text-foreground">{es.analytics.topQueries.title}</h2>
      <p className="mt-1 text-[13px] text-muted">{es.analytics.topQueries.subtitle}</p>
      <div className="mt-4 overflow-hidden rounded-2xl border border-border-subtle bg-surface-elevated">
        <table className="min-w-full text-left text-[13px]">
          <thead className="border-b border-border-subtle bg-surface-subtle/60 text-[11px] uppercase tracking-[0.12em] text-muted-light">
            <tr>
              <th className="px-4 py-3 font-medium">{es.common.question}</th>
              <th className="px-4 py-3 font-medium">{es.common.count}</th>
              <th className="px-4 py-3 font-medium">{es.common.channel}</th>
              <th className="px-4 py-3 font-medium">{es.analytics.topQueries.successRate}</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && topQueries.length === 0 ? (
              <tr>
                <td className="px-4 py-6 text-muted" colSpan={4}>
                  {es.common.loading}
                </td>
              </tr>
            ) : topQueries.length === 0 ? (
              <tr>
                <td className="px-4 py-6 text-muted" colSpan={4}>
                  {es.common.noData}
                </td>
              </tr>
            ) : (
              topQueries.map((item) => (
                <tr key={`${item.question}-${item.route}`} className="border-t border-border-subtle">
                  <td className="px-4 py-3 text-foreground/90">{item.question}</td>
                  <td className="px-4 py-3 text-muted">{formatter.format(item.count)}</td>
                  <td className="px-4 py-3 text-muted">{translateHandledBy(item.route)}</td>
                  <td className="px-4 py-3 text-muted">
                    {(item.success_rate * 100).toFixed(1)}%
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  )
}
