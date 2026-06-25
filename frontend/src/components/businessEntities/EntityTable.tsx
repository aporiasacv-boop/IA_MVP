import type { BusinessEntityItem, EntitySortField } from '../../types/businessEntities'
import { es } from '../../i18n/spanish'

interface Props {
  items: BusinessEntityItem[]
  total: number
  page: number
  pageSize: number
  sortBy: EntitySortField
  sortDir: 'asc' | 'desc'
  isLoading: boolean
  onSort: (field: EntitySortField) => void
  onPageChange: (page: number) => void
}

function formatAmount(value: string): string {
  const num = Number(value)
  if (Number.isNaN(num)) return value
  return new Intl.NumberFormat('es-MX', {
    style: 'currency',
    currency: 'MXN',
    maximumFractionDigits: 0,
  }).format(num)
}

const columns: { key: EntitySortField; label: string }[] = [
  { key: 'entity_code', label: es.businessEntities.table.code },
  { key: 'entity_name', label: es.businessEntities.table.name },
  { key: 'movement_count', label: es.businessEntities.table.movements },
  { key: 'movement_amount', label: es.businessEntities.table.amount },
]

export function EntityTable({
  items,
  total,
  page,
  pageSize,
  sortBy,
  sortDir,
  isLoading,
  onSort,
  onPageChange,
}: Props) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize))

  return (
    <section>
      <h2 className="text-[15px] font-semibold text-foreground">{es.businessEntities.table.title}</h2>
      <p className="mt-1 text-[12px] text-muted">{es.businessEntities.table.subtitle}</p>

      <div className="mt-4 overflow-x-auto rounded-xl border border-border-subtle">
        <table className="min-w-full text-left text-[12px]">
          <thead className="bg-surface-subtle text-muted">
            <tr>
              {columns.map((col) => (
                <th key={col.key} className="px-3 py-2 font-medium">
                  <button
                    type="button"
                    onClick={() => onSort(col.key)}
                    className="inline-flex items-center gap-1 hover:text-foreground"
                  >
                    {col.label}
                    {sortBy === col.key ? (sortDir === 'asc' ? ' ↑' : ' ↓') : null}
                  </button>
                </th>
              ))}
              <th className="px-3 py-2 font-medium">{es.businessEntities.table.source}</th>
              <th className="px-3 py-2 font-medium">{es.businessEntities.table.status}</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && items.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-3 py-6 text-center text-muted">
                  {es.common.loading}
                </td>
              </tr>
            ) : items.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-3 py-6 text-center text-muted">
                  {es.common.noData}
                </td>
              </tr>
            ) : (
              items.map((item) => (
                <tr key={item.entity_id} className="border-t border-border-subtle">
                  <td className="px-3 py-2 font-mono text-[11px]">{item.entity_code}</td>
                  <td className="max-w-[16rem] truncate px-3 py-2" title={item.entity_name}>
                    {item.entity_name}
                  </td>
                  <td className="px-3 py-2 tabular-nums">{item.movement_count.toLocaleString('es-MX')}</td>
                  <td className="px-3 py-2 tabular-nums">{formatAmount(item.movement_amount)}</td>
                  <td className="px-3 py-2 text-[11px] text-muted">{item.source_column}</td>
                  <td className="px-3 py-2 text-[11px]">{item.classification_status}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="mt-3 flex items-center justify-between text-[11px] text-muted">
        <span>
          {es.businessEntities.table.showing} {(page - 1) * pageSize + 1}–
          {Math.min(page * pageSize, total)} {es.businessEntities.table.of} {total}
        </span>
        <div className="flex gap-2">
          <button
            type="button"
            disabled={page <= 1 || isLoading}
            onClick={() => onPageChange(page - 1)}
            className="rounded border border-border-subtle px-2 py-1 disabled:opacity-40"
          >
            {es.businessEntities.table.prev}
          </button>
          <button
            type="button"
            disabled={page >= totalPages || isLoading}
            onClick={() => onPageChange(page + 1)}
            className="rounded border border-border-subtle px-2 py-1 disabled:opacity-40"
          >
            {es.businessEntities.table.next}
          </button>
        </div>
      </div>
    </section>
  )
}
