import { ProfileDetailPanel, ProfileListTable } from '../components/entityProfiles/ProfileTables'
import { ProfileStatisticsSection } from '../components/entityProfiles/ProfileStatisticsSection'
import { useEntityProfiles } from '../hooks/useEntityProfiles'
import { es } from '../i18n/spanish'

export function EntityProfilesPage() {
  const { profiles, statistics, selected, search, setSearch, isLoading, error, refresh, selectProfile } =
    useEntityProfiles()

  return (
    <div className="h-full overflow-y-auto px-4 py-8 md:px-8 md:py-10">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-muted-light">
            {es.entityProfiles.eyebrow}
          </p>
          <h1 className="mt-3 text-2xl font-semibold tracking-[-0.03em]">{es.entityProfiles.title}</h1>
          <p className="mt-2 max-w-2xl text-[13px] text-muted">{es.entityProfiles.subtitle}</p>
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
        <ProfileStatisticsSection statistics={statistics} isLoading={isLoading} />
        <input
          type="search"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder={es.entityProfiles.filters.searchPlaceholder}
          className="w-full max-w-md rounded-lg border border-border-subtle bg-surface-elevated px-3 py-2 text-[12px]"
        />
        <div className="grid gap-8 lg:grid-cols-2">
          <ProfileListTable
            items={profiles?.items ?? []}
            selectedId={selected?.canonical_id}
            isLoading={isLoading}
            onSelect={(id) => void selectProfile(id)}
          />
          <ProfileDetailPanel profile={selected} isLoading={isLoading} />
        </div>
      </div>
    </div>
  )
}
