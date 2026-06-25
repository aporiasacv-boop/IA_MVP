import type { TopRouteItem } from '../../types/operationalAudit'
import { es, translateHandledBy } from '../../i18n/spanish'

interface TopRoutesTableProps {
  items: TopRouteItem[]
  isLoading?: boolean
}

export function TopRoutesTable({ items, isLoading = false }: TopRoutesTableProps) {
  return (
    <section>
      <h2 className="text-lg font-semibold text-foreground">{es.audit.topRoutes.title}</h2>
      <p className="mt-1 text-[13px] text-muted">{es.audit.topRoutes.subtitle}</p>
      <div className="mt-4 overflow-x-auto rounded-2xl border border-border-subtle">
        <table className="w-full min-w-[24rem] text-left text-[13px]">
          <thead className="border-b border-border-subtle bg-surface-elevated text-muted">
            <tr>
              <th className="px-4 py-3 font-medium">{es.common.channel}</th>
              <th className="px-4 py-3 font-medium">{es.common.count}</th>
              <th className="px-4 py-3 font-medium">{es.common.percent}</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={3} className="px-4 py-6 text-center text-muted">
                  {es.common.loading}
                </td>
              </tr>
            ) : items.length === 0 ? (
              <tr>
                <td colSpan={3} className="px-4 py-6 text-center text-muted">
                  {es.common.noData}
                </td>
              </tr>
            ) : (
              items.map((item) => (
                <tr key={item.route} className="border-t border-border-subtle">
                  <td className="px-4 py-3 text-foreground">{translateHandledBy(item.route)}</td>
                  <td className="px-4 py-3 text-muted">{item.count}</td>
                  <td className="px-4 py-3 text-muted">{item.percentage.toFixed(1)}%</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  )
}
