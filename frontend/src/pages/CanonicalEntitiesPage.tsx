import { CanonicalStatisticsSection } from '../components/canonicalEntities/CanonicalStatisticsSection'
import {
  CanonicalEntitiesTable,
  CanonicalSuggestionsTable,
} from '../components/canonicalEntities/CanonicalTables'
import { useCanonicalEntities } from '../hooks/useCanonicalEntities'
import { es } from '../i18n/spanish'

export function CanonicalEntitiesPage() {
  const { canonicals, suggestions, statistics, search, setSearch, isLoading, error, refresh } =
    useCanonicalEntities()

  return (
    <div className="h-full overflow-y-auto px-4 py-8 md:px-8 md:py-10">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-muted-light">
            {es.canonicalEntities.eyebrow}
          </p>
          <h1 className="mt-3 text-2xl font-semibold tracking-[-0.03em]">{es.canonicalEntities.title}</h1>
          <p className="mt-2 max-w-2xl text-[13px] text-muted">{es.canonicalEntities.subtitle}</p>
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
        <CanonicalStatisticsSection statistics={statistics} isLoading={isLoading} />
        <input
          type="search"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder={es.canonicalEntities.filters.searchPlaceholder}
          className="w-full max-w-md rounded-lg border border-border-subtle bg-surface-elevated px-3 py-2 text-[12px]"
        />
        <CanonicalEntitiesTable items={canonicals?.items ?? []} isLoading={isLoading} />
        <CanonicalSuggestionsTable items={suggestions?.items ?? []} isLoading={isLoading} />
      </div>
    </div>
  )
}
