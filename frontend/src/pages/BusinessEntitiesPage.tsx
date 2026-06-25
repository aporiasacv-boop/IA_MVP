import { EntityStatisticsSection } from '../components/businessEntities/EntityStatisticsSection'
import { EntityTable } from '../components/businessEntities/EntityTable'
import { useBusinessEntities } from '../hooks/useBusinessEntities'
import { es } from '../i18n/spanish'
import type { EntitySortField } from '../types/businessEntities'

const SOURCE_OPTIONS = [
  { value: '', label: es.businessEntities.filters.allSources },
  { value: 'account_display_value', label: es.businessEntities.filters.account },
  { value: 'cuenta_proveedor', label: es.businessEntities.filters.vendor },
  { value: 'cuenta_cliente', label: es.businessEntities.filters.customer },
]

export function BusinessEntitiesPage() {
  const { list, statistics, params, isLoading, error, refresh, updateParams } = useBusinessEntities()

  const handleSort = (field: EntitySortField) => {
    const nextDir =
      params.sort_by === field && params.sort_dir === 'desc' ? 'asc' : 'desc'
    updateParams({ sort_by: field, sort_dir: nextDir, page: 1 })
  }

  return (
    <div className="h-full overflow-y-auto px-4 py-8 md:px-8 md:py-10">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-muted-light">
            {es.businessEntities.eyebrow}
          </p>
          <h1 className="mt-3 text-2xl font-semibold tracking-[-0.03em] text-foreground">
            {es.businessEntities.title}
          </h1>
          <p className="mt-2 max-w-2xl text-[13px] text-muted">{es.businessEntities.subtitle}</p>
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

      <div className="mt-10 space-y-10">
        <EntityStatisticsSection statistics={statistics} isLoading={isLoading} />

        <div className="flex flex-wrap gap-3">
          <input
            type="search"
            value={params.search ?? ''}
            placeholder={es.businessEntities.filters.searchPlaceholder}
            onChange={(event) => updateParams({ search: event.target.value, page: 1 })}
            className="min-w-[14rem] flex-1 rounded-lg border border-border-subtle bg-surface-elevated px-3 py-2 text-[12px]"
          />
          <select
            value={params.source_column ?? ''}
            onChange={(event) =>
              updateParams({ source_column: event.target.value || undefined, page: 1 })
            }
            className="rounded-lg border border-border-subtle bg-surface-elevated px-3 py-2 text-[12px]"
          >
            {SOURCE_OPTIONS.map((option) => (
              <option key={option.value || 'all'} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <select
            value={params.classification_status ?? ''}
            onChange={(event) =>
              updateParams({
                classification_status: event.target.value || undefined,
                page: 1,
              })
            }
            className="rounded-lg border border-border-subtle bg-surface-elevated px-3 py-2 text-[12px]"
          >
            <option value="">{es.businessEntities.filters.allStatuses}</option>
            <option value="pending">pending</option>
          </select>
        </div>

        <EntityTable
          items={list?.items ?? []}
          total={list?.total ?? 0}
          page={params.page ?? 1}
          pageSize={params.page_size ?? 50}
          sortBy={params.sort_by ?? 'movement_count'}
          sortDir={params.sort_dir ?? 'desc'}
          isLoading={isLoading}
          onSort={handleSort}
          onPageChange={(page) => updateParams({ page })}
        />
      </div>
    </div>
  )
}
