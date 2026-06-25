import {
  KnowledgeDetailPanel,
  KnowledgeEntityList,
  KnowledgeStatisticsSection,
} from '../components/enterpriseKnowledge/KnowledgePanels'
import { useEnterpriseKnowledge } from '../hooks/useEnterpriseKnowledge'
import { es } from '../i18n/spanish'

export function EnterpriseKnowledgePage() {
  const { list, statistics, selected, selectEntity, search, setSearch, isLoading, error, refresh } =
    useEnterpriseKnowledge()

  return (
    <div className="h-full overflow-y-auto px-4 py-8 md:px-8 md:py-10">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-muted-light">
            {es.enterpriseKnowledge.eyebrow}
          </p>
          <h1 className="mt-3 text-2xl font-semibold tracking-[-0.03em]">{es.enterpriseKnowledge.title}</h1>
          <p className="mt-2 max-w-2xl text-[13px] text-muted">{es.enterpriseKnowledge.subtitle}</p>
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
        <KnowledgeStatisticsSection statistics={statistics} isLoading={isLoading} />
        <input
          type="search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder={es.enterpriseKnowledge.filters.searchPlaceholder}
          className="w-full max-w-md rounded-lg border border-border-subtle bg-surface-elevated px-3 py-2 text-[12px]"
        />
        <div className="grid gap-8 lg:grid-cols-2">
          <KnowledgeEntityList
            items={list?.items ?? []}
            selectedId={selected?.canonical_id}
            isLoading={isLoading}
            onSelect={(id) => void selectEntity(id)}
          />
          <KnowledgeDetailPanel entity={selected} />
        </div>
      </div>
    </div>
  )
}
