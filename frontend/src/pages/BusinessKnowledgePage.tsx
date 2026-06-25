import { useEnterpriseKnowledge } from '../hooks/useEnterpriseKnowledge'
import { es } from '../i18n/spanish'

const CATEGORY_ORDER = ['concepts', 'faq', 'rules', 'scenarios', 'glossary', 'examples', 'executive']

export function BusinessKnowledgePage() {
  const {
    statistics,
    health,
    providers,
    categories,
    search,
    setSearch,
    results,
    isLoading,
    error,
    refresh,
  } = useEnterpriseKnowledge()

  const sortedCategories = [...(categories?.categories ?? [])].sort(
    (a, b) => CATEGORY_ORDER.indexOf(a.category) - CATEGORY_ORDER.indexOf(b.category),
  )

  return (
    <div className="h-full overflow-y-auto px-4 py-8 md:px-8 md:py-10">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-muted-light">
            {es.enterpriseKnowledgeService.eyebrow}
          </p>
          <h1 className="mt-3 text-2xl font-semibold tracking-[-0.03em]">
            {es.enterpriseKnowledgeService.title}
          </h1>
          <p className="mt-2 max-w-2xl text-[13px] text-muted">{es.enterpriseKnowledgeService.subtitle}</p>
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

      <div className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <StatCard label={es.enterpriseKnowledgeService.stats.documents} value={statistics?.total_documents} />
        <StatCard label={es.enterpriseKnowledgeService.stats.faq} value={statistics?.faq_entries} />
        <StatCard
          label={es.enterpriseKnowledgeService.stats.cacheStatus}
          valueText={health?.cache_valid ? es.enterpriseKnowledgeService.stats.cacheOk : es.enterpriseKnowledgeService.stats.cacheDegraded}
        />
        <StatCard
          label={es.enterpriseKnowledgeService.stats.reloadTime}
          valueText={health?.reload_time_ms != null ? `${health.reload_time_ms} ms` : '—'}
        />
        <StatCard
          label={es.enterpriseKnowledgeService.stats.cacheHitRate}
          valueText={health?.cache_hit_rate != null ? `${(health.cache_hit_rate * 100).toFixed(1)}%` : '—'}
        />
      </div>

      <section className="mt-10">
        <h2 className="text-[13px] font-semibold uppercase tracking-[0.14em] text-muted-light">
          {es.enterpriseKnowledgeService.providersTitle}
        </h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {(providers?.active ?? []).map((provider) => (
            <article
              key={provider.id}
              className="rounded-xl border border-border-subtle bg-surface-elevated/70 px-4 py-4"
            >
              <p className="text-[11px] uppercase tracking-[0.12em] text-emerald-700">
                {es.enterpriseKnowledgeService.providerActive}
              </p>
              <h3 className="mt-1 text-[15px] font-medium">{provider.name}</h3>
              <p className="mt-2 text-[13px] text-muted">
                {provider.document_count} {es.enterpriseKnowledgeService.documentsLabel}
              </p>
            </article>
          ))}
          {(providers?.planned ?? []).map((provider) => (
            <article
              key={provider.id}
              className="rounded-xl border border-dashed border-border-subtle bg-surface-elevated/40 px-4 py-4"
            >
              <p className="text-[11px] uppercase tracking-[0.12em] text-muted-light">
                {es.enterpriseKnowledgeService.providerPlanned}
              </p>
              <h3 className="mt-1 text-[15px] font-medium text-muted">{provider.name}</h3>
            </article>
          ))}
        </div>
      </section>

      <div className="mt-8">
        <input
          type="search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder={es.enterpriseKnowledgeService.searchPlaceholder}
          className="w-full max-w-xl rounded-lg border border-border-subtle bg-surface-elevated px-3 py-2 text-[13px]"
        />
      </div>

      {search.trim() && (
        <section className="mt-8">
          <h2 className="text-[13px] font-semibold uppercase tracking-[0.14em] text-muted-light">
            {es.enterpriseKnowledgeService.searchResults}
          </h2>
          <ul className="mt-4 space-y-3">
            {results.map((item) => (
              <li key={item.path} className="rounded-xl border border-border-subtle bg-surface-elevated/70 p-4">
                <p className="text-[12px] uppercase tracking-[0.12em] text-muted-light">{item.category}</p>
                <h3 className="mt-1 text-[15px] font-medium">{item.title}</h3>
                <p className="mt-2 line-clamp-4 text-[13px] text-muted">{item.content.slice(0, 280)}…</p>
              </li>
            ))}
            {results.length === 0 && (
              <p className="text-[13px] text-muted">{es.enterpriseKnowledgeService.noResults}</p>
            )}
          </ul>
        </section>
      )}

      <section className="mt-10">
        <h2 className="text-[13px] font-semibold uppercase tracking-[0.14em] text-muted-light">
          {es.enterpriseKnowledgeService.categoriesTitle}
        </h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {sortedCategories.map((category) => (
            <article
              key={category.category}
              className="rounded-xl border border-border-subtle bg-surface-elevated/70 px-4 py-4"
            >
              <h3 className="text-[15px] font-medium">{category.label}</h3>
              <p className="mt-2 text-[13px] text-muted">
                {category.count} {es.enterpriseKnowledgeService.documentsLabel}
              </p>
            </article>
          ))}
        </div>
      </section>
    </div>
  )
}

function StatCard({
  label,
  value,
  valueText,
}: {
  label: string
  value?: number
  valueText?: string
}) {
  return (
    <div className="rounded-xl border border-border-subtle bg-surface-elevated/70 px-4 py-4">
      <p className="text-[11px] uppercase tracking-[0.12em] text-muted-light">{label}</p>
      <p className="mt-2 text-2xl font-semibold tabular-nums">{valueText ?? value ?? '—'}</p>
    </div>
  )
}
