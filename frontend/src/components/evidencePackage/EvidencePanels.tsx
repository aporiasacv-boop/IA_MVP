import type { EnterpriseEvidencePackage, EvidenceStatistics } from '../../types/evidencePackage'
import { es } from '../../i18n/spanish'

export function EvidenceStatisticsSection({
  statistics,
  isLoading,
}: {
  statistics: EvidenceStatistics | null
  isLoading: boolean
}) {
  const cards = [
    { label: es.evidencePackage.stats.packages, value: statistics?.evidence_packages_total ?? '—' },
    { label: es.evidencePackage.stats.size, value: statistics?.average_package_size?.toFixed(0) ?? '—' },
    { label: es.evidencePackage.stats.items, value: statistics?.average_evidence_items?.toFixed(1) ?? '—' },
    {
      label: es.evidencePackage.stats.confidence,
      value: statistics ? `${(statistics.average_confidence * 100).toFixed(1)}%` : '—',
    },
    { label: es.evidencePackage.stats.missing, value: statistics?.missing_evidence ?? '—' },
  ]

  return (
    <section>
      <h2 className="text-[13px] font-semibold">{es.evidencePackage.stats.title}</h2>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {cards.map((card) => (
          <div key={card.label} className="rounded-xl border border-border-subtle bg-surface-elevated px-4 py-3">
            <p className="text-[11px] text-muted">{card.label}</p>
            <p className="mt-1 text-xl font-semibold tabular-nums">
              {isLoading ? es.common.loading : card.value}
            </p>
          </div>
        ))}
      </div>
    </section>
  )
}

export function EvidencePackagePanel({ pkg }: { pkg: EnterpriseEvidencePackage | null }) {
  if (!pkg) {
    return <p className="text-[12px] text-muted">{es.evidencePackage.detail.empty}</p>
  }

  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-[13px] font-semibold">{es.evidencePackage.detail.title}</h2>
        <p className="mt-2 text-[12px] font-medium">{pkg.question}</p>
        <p className="mt-1 text-[11px] text-muted">
          {es.evidencePackage.detail.strategy}: {pkg.execution_plan.execution_strategy} ·{' '}
          {es.evidencePackage.detail.confidence}:{' '}
          {(parseFloat(pkg.confidence.average_confidence) * 100).toFixed(1)}%
        </p>
      </div>

      <ItemTable title={es.evidencePackage.detail.knowledge} items={pkg.knowledge} />
      <ItemTable title={es.evidencePackage.detail.reasoning} items={pkg.reasoning} />
      <ItemTable title={es.evidencePackage.detail.facts} items={pkg.facts} />
      <ItemTable title={es.evidencePackage.detail.recommendations} items={pkg.recommendations} />

      {pkg.evidence.length > 0 && (
        <div>
          <h3 className="text-[12px] font-semibold">{es.evidencePackage.detail.evidence}</h3>
          <pre className="mt-2 max-h-48 overflow-auto rounded-lg border border-border-subtle bg-surface-elevated p-3 text-[10px]">
            {JSON.stringify(pkg.evidence, null, 2)}
          </pre>
        </div>
      )}

      {pkg.limitations.length > 0 && (
        <div>
          <h3 className="text-[12px] font-semibold">{es.evidencePackage.detail.limitations}</h3>
          <ul className="mt-2 space-y-1 text-[11px] text-amber-800">
            {pkg.limitations.map((lim) => (
              <li key={lim.code} className="rounded border border-amber-200 bg-amber-50 px-2 py-1">
                [{lim.severity}] {lim.code}: {lim.description}
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  )
}

function ItemTable({
  title,
  items,
}: {
  title: string
  items: Array<{ key: string; source: string; confidence: string }>
}) {
  if (items.length === 0) return null
  return (
    <div>
      <h3 className="text-[12px] font-semibold">{title}</h3>
      <div className="mt-2 overflow-x-auto rounded-lg border border-border-subtle">
        <table className="min-w-full text-left text-[11px]">
          <thead className="bg-surface-elevated text-muted">
            <tr>
              <th className="px-2 py-1.5">{es.evidencePackage.detail.tableKey}</th>
              <th className="px-2 py-1.5">{es.evidencePackage.detail.tableSource}</th>
              <th className="px-2 py-1.5">{es.evidencePackage.detail.tableConfidence}</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.key} className="border-t border-border-subtle/60">
                <td className="px-2 py-1.5 font-medium">{item.key}</td>
                <td className="px-2 py-1.5">{item.source}</td>
                <td className="px-2 py-1.5 tabular-nums">
                  {(parseFloat(item.confidence) * 100).toFixed(0)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
