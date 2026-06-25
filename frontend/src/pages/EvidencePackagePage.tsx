import { EvidencePackagePanel, EvidenceStatisticsSection } from '../components/evidencePackage/EvidencePanels'
import { useEvidencePackage } from '../hooks/useEvidencePackage'
import { es } from '../i18n/spanish'

export function EvidencePackagePage() {
  const { question, setQuestion, package: pkg, statistics, samples, isLoading, error, build, loadExample } =
    useEvidencePackage()

  return (
    <div className="h-full overflow-y-auto px-4 py-8 md:px-8 md:py-10">
      <div>
        <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-muted-light">
          {es.evidencePackage.eyebrow}
        </p>
        <h1 className="mt-3 text-2xl font-semibold tracking-[-0.03em]">{es.evidencePackage.title}</h1>
        <p className="mt-2 max-w-2xl text-[13px] text-muted">{es.evidencePackage.subtitle}</p>
      </div>

      {error && (
        <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          {error}
        </div>
      )}

      <div className="mt-10 space-y-10">
        <EvidenceStatisticsSection statistics={statistics} isLoading={isLoading} />

        <div className="space-y-3">
          <label className="text-[12px] font-medium">{es.evidencePackage.form.label}</label>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows={2}
            className="w-full max-w-2xl rounded-lg border border-border-subtle bg-surface-elevated px-3 py-2 text-[12px]"
          />
          <div className="flex flex-wrap gap-2">
            {samples.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => {
                  setQuestion(s)
                  void build(s)
                }}
                className="rounded-full border border-border-subtle px-3 py-1 text-[10px] text-muted hover:text-foreground"
              >
                {s.slice(0, 35)}…
              </button>
            ))}
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => void build(question)}
              disabled={isLoading}
              className="rounded-lg border border-border-subtle bg-surface-elevated px-3 py-2 text-[12px] font-medium"
            >
              {isLoading ? es.common.loading : es.evidencePackage.form.build}
            </button>
            <button
              type="button"
              onClick={() => void loadExample()}
              disabled={isLoading}
              className="rounded-lg border border-border-subtle px-3 py-2 text-[12px] text-muted"
            >
              {es.evidencePackage.form.example}
            </button>
          </div>
        </div>

        <EvidencePackagePanel pkg={pkg} />
      </div>
    </div>
  )
}
