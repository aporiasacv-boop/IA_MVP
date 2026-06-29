import type { ChatMessage } from '../../types/chat'
import { es } from '../../i18n/spanish'

interface EnterpriseEvidencePlannerDebugProps {
  message: ChatMessage
}

export function EnterpriseEvidencePlannerDebug({ message }: EnterpriseEvidencePlannerDebugProps) {
  const metadata = message.hybrid?.rawMetadata
  const plan = metadata?.enterprise_evidence_plan as
    | {
        business_goal?: string
        required_evidence?: string[]
        required_capabilities?: string[]
        estimated_coverage?: number
        execution_order?: string[]
      }
    | undefined

  if (!plan && !metadata?.business_goal) return null

  const goal = plan?.business_goal ?? metadata?.business_goal ?? '—'
  const evidence = plan?.required_evidence ?? metadata?.required_evidence ?? []
  const capabilities = plan?.required_capabilities ?? metadata?.required_capabilities ?? []
  const coverage = plan?.estimated_coverage ?? metadata?.estimated_coverage ?? '—'

  return (
    <div className="mt-4 rounded-xl border border-emerald-200/70 bg-emerald-50/35 px-4 py-3">
      <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-emerald-900/80">
        {es.evidencePlanner.title}
      </p>
      <dl className="mt-3 grid gap-3 sm:grid-cols-2">
        <div className="sm:col-span-2">
          <dt className="text-[10px] uppercase tracking-[0.12em] text-muted-light">
            {es.evidencePlanner.goal}
          </dt>
          <dd className="mt-1 text-[13px] font-medium text-foreground/85">{String(goal)}</dd>
        </div>
        <div>
          <dt className="text-[10px] uppercase tracking-[0.12em] text-muted-light">
            {es.evidencePlanner.coverage}
          </dt>
          <dd className="mt-1 text-[13px] font-medium text-foreground/85">
            {typeof coverage === 'number' ? `${coverage}%` : String(coverage)}
          </dd>
        </div>
      </dl>
      {Array.isArray(evidence) && evidence.length > 0 && (
        <div className="mt-3">
          <p className="text-[10px] uppercase tracking-[0.12em] text-muted-light">
            {es.evidencePlanner.evidence}
          </p>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-[12px] text-foreground/85">
            {evidence.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      )}
      {Array.isArray(capabilities) && capabilities.length > 0 && (
        <div className="mt-3">
          <p className="text-[10px] uppercase tracking-[0.12em] text-muted-light">
            {es.evidencePlanner.capabilities}
          </p>
          <p className="mt-1 text-[12px] text-foreground/85">{capabilities.join(' · ')}</p>
        </div>
      )}
    </div>
  )
}
