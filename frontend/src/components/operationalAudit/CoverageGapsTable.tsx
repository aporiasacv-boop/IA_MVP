import type { CoverageGapItem } from '../../types/operationalAudit'
import { es } from '../../i18n/spanish'
import { translateHandledBy } from '../../i18n/spanish'

interface CoverageGapsTableProps {
  items: CoverageGapItem[]
  isLoading?: boolean
  onExportJson?: () => void
  onExportCsv?: () => void
  isExporting?: boolean
}

export function CoverageGapsTable({
  items,
  isLoading = false,
  onExportJson,
  onExportCsv,
  isExporting = false,
}: CoverageGapsTableProps) {
  return (
    <section>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-foreground">{es.audit.coverageGaps.title}</h2>
          <p className="mt-1 text-[13px] text-muted">{es.audit.coverageGaps.subtitle}</p>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={onExportJson}
            disabled={isExporting || isLoading}
            className="rounded-lg border border-border-subtle bg-surface-elevated px-3 py-2 text-[12px] font-medium text-muted hover:text-foreground disabled:opacity-50"
          >
            {es.common.exportJson}
          </button>
          <button
            type="button"
            onClick={onExportCsv}
            disabled={isExporting || isLoading}
            className="rounded-lg border border-border-subtle bg-surface-elevated px-3 py-2 text-[12px] font-medium text-muted hover:text-foreground disabled:opacity-50"
          >
            {es.common.exportCsv}
          </button>
        </div>
      </div>
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
                  <td className="px-4 py-3 text-muted">{item.count}</td>
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
