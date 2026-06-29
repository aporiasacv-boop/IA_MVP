import type { BusinessCopilotProposal, ChatMessage } from '../../types/chat'
import { es } from '../../i18n/spanish'

interface BusinessCopilotPanelProps {
  message: ChatMessage
  onSelectProposal?: (query: string) => void
  disabled?: boolean
}

function readProposals(metadata: Record<string, unknown> | undefined): BusinessCopilotProposal[] {
  const raw = metadata?.business_copilot_proposals
  if (!Array.isArray(raw)) return []

  return raw
    .map((item) => {
      if (!item || typeof item !== 'object') return null
      const payload = item as Record<string, unknown>
      const title = typeof payload.title === 'string' ? payload.title.trim() : ''
      const rationale = typeof payload.rationale === 'string' ? payload.rationale.trim() : ''
      const actionLabel =
        typeof payload.action_label === 'string' ? payload.action_label.trim() : ''
      const query = typeof payload.query === 'string' ? payload.query.trim() : ''
      const proposalType =
        typeof payload.proposal_type === 'string' ? payload.proposal_type.trim() : ''
      if (!title || !rationale || !actionLabel || !query) return null
      return {
        title,
        rationale,
        actionLabel,
        query,
        proposalType,
      }
    })
    .filter((item): item is BusinessCopilotProposal => item !== null)
}

function ProposalCard({
  proposal,
  onSelect,
  disabled,
}: {
  proposal: BusinessCopilotProposal
  onSelect?: (query: string) => void
  disabled?: boolean
}) {
  return (
    <article className="rounded-xl border border-border-subtle bg-surface-elevated/70 px-4 py-4">
      <h3 className="text-[15px] font-semibold text-foreground/90">{proposal.title}</h3>
      <p className="mt-2 text-[12px] font-medium uppercase tracking-[0.1em] text-muted-light">
        {es.businessCopilot.why}
      </p>
      <p className="mt-1 text-[14px] leading-6 text-foreground/80">{proposal.rationale}</p>
      {onSelect && (
        <button
          type="button"
          disabled={disabled}
          onClick={() => onSelect(proposal.query)}
          className="transition-premium mt-4 rounded-lg bg-olnatura-700 px-4 py-2 text-[13px] font-medium text-white hover:bg-olnatura-800 disabled:opacity-40"
        >
          {proposal.actionLabel}
        </button>
      )}
    </article>
  )
}

export function BusinessCopilotPanel({
  message,
  onSelectProposal,
  disabled = false,
}: BusinessCopilotPanelProps) {
  const proposals = readProposals(message.hybrid?.rawMetadata)
  if (proposals.length === 0) return null

  return (
    <section className="mt-5">
      <h2 className="text-[12px] font-semibold uppercase tracking-[0.14em] text-foreground/80">
        {es.businessCopilot.title}
      </h2>
      <div className="mt-4 space-y-3">
        {proposals.map((proposal) => (
          <ProposalCard
            key={`${proposal.title}-${proposal.query}`}
            proposal={proposal}
            onSelect={onSelectProposal}
            disabled={disabled}
          />
        ))}
      </div>
    </section>
  )
}
