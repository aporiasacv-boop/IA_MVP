import type { TopFailureItem } from '../../types/operationalAudit'
import { es, translateHandledBy } from '../../i18n/spanish'

interface TopFailuresTableProps {
  items: TopFailureItem[]
  isLoading?: boolean
}

export function TopFailuresTable({ items, isLoading = false }: TopFailuresTableProps) {
  return (
    <section>
      <h2 className="text-lg font-semibold text-foreground">{es.audit.topFailures.title}</h2>
      <p className="mt-1 text-[13px] text-muted">{es.audit.topFailures.subtitle}</p>
      <div className="mt-4 overflow-x-auto rounded-2xl border border-border-subtle">
        <table className="w-full min-w-[32rem] text-left text-[13px]">
          <thead className="border-b border-border-subtle bg-surface-elevated text-muted">
            <tr>
              <th className="px-4 py-3 font-medium">{es.common.question}</th>
              <th className="px-4 py-3 font-medium">{es.common.count}</th>
              <th className="px-4 py-3 font-medium">{es.common.channel}</th>
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
              items.map((item, index) => (
                <tr key={`${item.question}-${item.route}-${index}`} className="border-t border-border-subtle">
                  <td className="px-4 py-3 text-foreground">{item.question}</td>
                  <td className="px-4 py-3 text-muted">{item.frequency}</td>
                  <td className="px-4 py-3 text-muted">{translateHandledBy(item.route)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  )
}
