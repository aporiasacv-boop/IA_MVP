import type { ChatMessage } from '../../types/chat'
import { es } from '../../i18n/spanish'

interface EnterpriseEvidencePackageDebugProps {
  message: ChatMessage
}

export function EnterpriseEvidencePackageDebug({ message }: EnterpriseEvidencePackageDebugProps) {
  const metadata = message.hybrid?.rawMetadata
  const pkg = metadata?.enterprise_evidence_package as
    | {
        business_goal?: string
        evidence_items?: Array<{
          evidence_label?: string
          capability?: string
          query_type?: string
          success?: boolean
        }>
        coverage?: number
        missing_evidence?: string[]
      }
    | undefined

  if (!pkg) return null

  const executed = metadata?.executed_capabilities ?? []
  const coverage = pkg.coverage ?? metadata?.package_coverage ?? '—'

  return (
    <div className="mt-4 rounded-xl border border-sky-200/70 bg-sky-50/35 px-4 py-3">
      <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-sky-900/80">
        {es.evidenceOrchestrator.title}
      </p>
      <dl className="mt-3 grid gap-3 sm:grid-cols-2">
        <div className="sm:col-span-2">
          <dt className="text-[10px] uppercase tracking-[0.12em] text-muted-light">
            {es.evidenceOrchestrator.goal}
          </dt>
          <dd className="mt-1 text-[13px] font-medium text-foreground/85">
            {String(pkg.business_goal ?? '—')}
          </dd>
        </div>
        <div>
          <dt className="text-[10px] uppercase tracking-[0.12em] text-muted-light">
            {es.evidenceOrchestrator.coverage}
          </dt>
          <dd className="mt-1 text-[13px] font-medium text-foreground/85">
            {typeof coverage === 'number' ? `${coverage}%` : String(coverage)}
          </dd>
        </div>
        <div>
          <dt className="text-[10px] uppercase tracking-[0.12em] text-muted-light">
            {es.evidenceOrchestrator.executed}
          </dt>
          <dd className="mt-1 text-[13px] font-medium text-foreground/85">
            {Array.isArray(executed) && executed.length > 0 ? executed.join(' · ') : '—'}
          </dd>
        </div>
      </dl>
      {Array.isArray(pkg.evidence_items) && pkg.evidence_items.length > 0 && (
        <div className="mt-3">
          <p className="text-[10px] uppercase tracking-[0.12em] text-muted-light">
            {es.evidenceOrchestrator.evidence}
          </p>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-[12px] text-foreground/85">
            {pkg.evidence_items.map((item, index) => (
              <li key={`${item.capability}-${index}`}>
                {item.evidence_label ?? item.capability} ({item.capability})
              </li>
            ))}
          </ul>
        </div>
      )}
      {Array.isArray(pkg.missing_evidence) && pkg.missing_evidence.length > 0 && (
        <div className="mt-3">
          <p className="text-[10px] uppercase tracking-[0.12em] text-muted-light">
            {es.evidenceOrchestrator.missing}
          </p>
          <p className="mt-1 text-[12px] text-foreground/85">{pkg.missing_evidence.join(' · ')}</p>
        </div>
      )}
    </div>
  )
}
