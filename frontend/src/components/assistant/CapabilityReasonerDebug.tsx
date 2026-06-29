import type { ChatMessage } from '../../types/chat'
import { es } from '../../i18n/spanish'

interface ReasonerCandidate {
  capability_id?: string
  score?: number
}

interface ReasonerPlanPayload {
  reasoning_goal?: string
  candidate_capabilities?: ReasonerCandidate[]
  selected_capabilities?: string[]
  estimated_coverage?: number
  recommended_plan?: string
  fallback_recommended?: boolean
}

interface CapabilityReasonerDebugProps {
  message: ChatMessage
}

function readPlan(message: ChatMessage): ReasonerPlanPayload | null {
  const raw = message.hybrid?.rawMetadata?.capability_reasoner_plan
  if (!raw || typeof raw !== 'object') return null
  return raw as ReasonerPlanPayload
}

export function CapabilityReasonerDebug({ message }: CapabilityReasonerDebugProps) {
  const metadata = message.hybrid?.rawMetadata
  const plan = readPlan(message)
  if (!plan && !metadata?.reasoning_goal) return null

  const goal = plan?.reasoning_goal ?? metadata?.reasoning_goal ?? '—'
  const coverage = plan?.estimated_coverage ?? metadata?.estimated_coverage ?? '—'
  const candidates = plan?.candidate_capabilities ?? metadata?.candidate_capabilities ?? []
  const topCandidates = Array.isArray(candidates) ? candidates.slice(0, 5) : []

  return (
    <div className="mt-4 rounded-xl border border-sky-200/70 bg-sky-50/40 px-4 py-3">
      <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-sky-900/80">
        {es.capabilityReasoner.title}
      </p>
      <dl className="mt-3 grid gap-3 sm:grid-cols-2">
        <div>
          <dt className="text-[10px] uppercase tracking-[0.12em] text-muted-light">
            {es.capabilityReasoner.goal}
          </dt>
          <dd className="mt-1 text-[13px] font-medium text-foreground/85">{String(goal)}</dd>
        </div>
        <div>
          <dt className="text-[10px] uppercase tracking-[0.12em] text-muted-light">
            {es.capabilityReasoner.coverage}
          </dt>
          <dd className="mt-1 text-[13px] font-medium text-foreground/85">
            {typeof coverage === 'number' ? `${coverage}%` : String(coverage)}
          </dd>
        </div>
      </dl>
      {topCandidates.length > 0 && (
        <div className="mt-3">
          <p className="text-[10px] uppercase tracking-[0.12em] text-muted-light">
            {es.capabilityReasoner.candidates}
          </p>
          <ul className="mt-2 space-y-1 text-[12px] text-foreground/85">
            {topCandidates.map((item) => (
              <li key={String(item.capability_id)}>
                {item.capability_id} — score: {item.score}
              </li>
            ))}
          </ul>
        </div>
      )}
      {(plan?.recommended_plan || metadata?.recommended_plan) && (
        <p className="mt-3 text-[13px] leading-6 text-foreground/85">
          {String(plan?.recommended_plan ?? metadata?.recommended_plan)}
        </p>
      )}
    </div>
  )
}
