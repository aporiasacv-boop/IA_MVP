import type { AdoptionMetrics } from '../../types/operationalAudit'
import { es } from '../../i18n/spanish'
import { AnalyticsCard } from '../analytics/AnalyticsCard'

const formatter = new Intl.NumberFormat('es-MX')

interface AdoptionSectionProps {
  adoption: AdoptionMetrics | null
  isLoading?: boolean
}

export function AdoptionSection({ adoption, isLoading = false }: AdoptionSectionProps) {
  const cards = adoption
    ? [
        {
          label: es.audit.adoption.suggestedQuestions,
          value: formatter.format(adoption.suggested_questions_usage),
        },
        {
          label: es.audit.adoption.conversationMemory,
          value: formatter.format(adoption.conversation_memory_usage),
        },
        {
          label: es.audit.adoption.slotClarification,
          value: formatter.format(adoption.slot_clarification_usage),
        },
        {
          label: es.audit.adoption.capabilityDiscovery,
          value: formatter.format(adoption.capability_discovery_usage),
        },
      ]
    : []

  return (
    <section>
      <h2 className="text-lg font-semibold text-foreground">{es.audit.adoption.title}</h2>
      <p className="mt-1 text-[13px] text-muted">{es.audit.adoption.subtitle}</p>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {isLoading && !adoption
          ? Array.from({ length: 4 }).map((_, index) => (
              <div
                key={index}
                className="animate-pulse rounded-2xl border border-border-subtle bg-surface-elevated px-4 py-5"
              >
                <div className="h-3 w-24 rounded bg-surface-subtle" />
                <div className="mt-4 h-8 w-16 rounded bg-surface-subtle" />
              </div>
            ))
          : cards.map((card) => <AnalyticsCard key={card.label} {...card} />)}
      </div>
    </section>
  )
}
