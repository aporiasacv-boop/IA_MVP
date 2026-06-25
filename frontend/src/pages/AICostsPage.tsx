import { AICostPanels } from '../components/aiCosts/AICostPanels'
import { useAICosts } from '../hooks/useAICosts'
import { es } from '../i18n/spanish'

export function AICostsPage() {
  const { data, isLoading, error, refresh } = useAICosts()

  return (
    <div className="h-full overflow-y-auto px-4 py-8 md:px-8 md:py-10">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-muted-light">
            {es.aiCosts.eyebrow}
          </p>
          <h1 className="mt-3 text-2xl font-semibold tracking-[-0.03em] text-foreground">
            {es.aiCosts.title}
          </h1>
          <p className="mt-2 max-w-2xl text-[13px] text-muted">{es.aiCosts.subtitle}</p>
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

      <div className="mt-10">
        <AICostPanels summary={data} isLoading={isLoading} />
      </div>
    </div>
  )
}
