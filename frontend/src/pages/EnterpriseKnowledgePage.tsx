import { useEnterpriseKnowledge } from '../hooks/useEnterpriseKnowledge'
import { es } from '../i18n/spanish'

export function EnterpriseKnowledgePage() {
  const { statistics, search, setSearch, results, isLoading, error, refresh } =
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

      <div className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label={es.enterpriseKnowledge.stats.objects} value={statistics?.total_documents} />
        <StatCard
          label={es.enterpriseKnowledgeService.stats.faq}
          value={statistics?.faq_entries}
        />
        <StatCard
          label={es.enterpriseKnowledgeService.stats.cacheHitRate}
          value={
            statistics?.cache_hit_rate != null
              ? `${(statistics.cache_hit_rate * 100).toFixed(0)}%`
              : undefined
          }
        />
        <StatCard
          label={es.enterpriseKnowledgeService.stats.reloadTime}
          value={
            statistics?.knowledge_runtime_reload_time_ms != null
              ? `${statistics.knowledge_runtime_reload_time_ms.toFixed(0)} ms`
              : undefined
          }
        />
      </div>

      <div className="mt-10">
        <input
          type="search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder={es.enterpriseKnowledge.filters.searchPlaceholder}
          className="w-full max-w-md rounded-lg border border-border-subtle bg-surface-elevated px-3 py-2 text-[12px]"
        />
        {search.trim() && (
          <ul className="mt-4 space-y-2">
            {results.length === 0 && !isLoading && (
              <li className="text-[13px] text-muted">{es.enterpriseKnowledgeService.noResults}</li>
            )}
            {results.map((doc) => (
              <li
                key={doc.id}
                className="rounded-xl border border-border-subtle bg-surface-elevated px-4 py-3"
              >
                <p className="text-[14px] font-medium text-foreground">{doc.title}</p>
                <p className="mt-1 text-[12px] text-muted">{doc.category}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

function StatCard({ label, value }: { label: string; value?: number | string }) {
  return (
    <div className="rounded-xl border border-border-subtle bg-surface-elevated px-4 py-3">
      <p className="text-[11px] font-medium uppercase tracking-[0.14em] text-muted-light">{label}</p>
      <p className="mt-2 text-xl font-semibold tabular-nums text-foreground">
        {value ?? '—'}
      </p>
    </div>
  )
}
