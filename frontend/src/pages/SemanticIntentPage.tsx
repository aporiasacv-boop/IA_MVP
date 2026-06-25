import { SemanticAnalysisPanel, SemanticStatisticsSection } from '../components/semanticIntent/SemanticPanels'
import { useSemanticIntent } from '../hooks/useSemanticIntent'
import { es } from '../i18n/spanish'

export function SemanticIntentPage() {
  const { question, setQuestion, parse, plan, statistics, sampleQuestions, isLoading, error, analyze } =
    useSemanticIntent()

  return (
    <div className="h-full overflow-y-auto px-4 py-8 md:px-8 md:py-10">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-muted-light">
            {es.semanticIntent.eyebrow}
          </p>
          <h1 className="mt-3 text-2xl font-semibold tracking-[-0.03em]">{es.semanticIntent.title}</h1>
          <p className="mt-2 max-w-2xl text-[13px] text-muted">{es.semanticIntent.subtitle}</p>
        </div>
      </div>

      {error && (
        <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          {error}
        </div>
      )}

      <div className="mt-10 space-y-10">
        <SemanticStatisticsSection statistics={statistics} isLoading={isLoading} />

        <div className="space-y-3">
          <label className="text-[12px] font-medium">{es.semanticIntent.form.label}</label>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows={3}
            className="w-full max-w-2xl rounded-lg border border-border-subtle bg-surface-elevated px-3 py-2 text-[12px]"
          />
          <div className="flex flex-wrap gap-2">
            {sampleQuestions.map((sample) => (
              <button
                key={sample}
                type="button"
                onClick={() => {
                  setQuestion(sample)
                  void analyze(sample)
                }}
                className="rounded-full border border-border-subtle px-3 py-1 text-[10px] text-muted hover:text-foreground"
              >
                {sample.slice(0, 40)}…
              </button>
            ))}
          </div>
          <button
            type="button"
            onClick={() => void analyze(question)}
            disabled={isLoading}
            className="rounded-lg border border-border-subtle bg-surface-elevated px-3 py-2 text-[12px] font-medium"
          >
            {isLoading ? es.common.loading : es.semanticIntent.form.analyze}
          </button>
        </div>

        <SemanticAnalysisPanel parse={parse} plan={plan} />
      </div>
    </div>
  )
}
