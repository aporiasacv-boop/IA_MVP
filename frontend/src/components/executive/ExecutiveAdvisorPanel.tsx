import type { ExecutiveAgendaItem, ExecutiveAgendaResponse } from '../../services/executiveAdvisorApi'
import { es } from '../../i18n/spanish'

interface ExecutiveAdvisorPanelProps {
  data: ExecutiveAgendaResponse | null
  isLoading?: boolean
  error?: string | null
  updatedFromConversation?: boolean
  onAnalyze?: (query: string) => void
  disabled?: boolean
  compact?: boolean
}

function PriorityBadge({ priority }: { priority: string }) {
  const normalized = priority.toLowerCase()
  const tone =
    normalized === 'alta'
      ? 'bg-red-100 text-red-800'
      : normalized === 'media'
        ? 'bg-amber-100 text-amber-900'
        : 'bg-surface-subtle text-muted'

  return (
    <span className={`rounded-full px-2.5 py-0.5 text-[11px] font-semibold uppercase ${tone}`}>
      {es.executiveAdvisor.priorityLabel}: {priority}
    </span>
  )
}

function AgendaCard({
  item,
  index,
  onAnalyze,
  disabled,
}: {
  item: ExecutiveAgendaItem
  index: number
  onAnalyze?: (query: string) => void
  disabled?: boolean
}) {
  return (
    <article className="rounded-xl border border-border-subtle bg-surface-elevated/80 px-4 py-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <p className="text-[11px] font-semibold text-olnatura-700">
            {String(index + 1).padStart(2, '0')}
          </p>
          <h3 className="mt-1 text-[15px] font-semibold text-foreground/90">{item.title}</h3>
        </div>
        <PriorityBadge priority={item.priority} />
      </div>
      <p className="mt-3 text-[14px] leading-6 text-foreground/85">{item.summary}</p>
      {item.justification.trim() && (
        <p className="mt-2 text-[13px] leading-6 text-muted">{item.justification}</p>
      )}
      {item.expected_impact.trim() && (
        <p className="mt-2 text-[12px] text-muted-light">{item.expected_impact}</p>
      )}
      {onAnalyze && (
        <button
          type="button"
          disabled={disabled}
          onClick={() => onAnalyze(item.suggested_query)}
          className="transition-premium mt-4 rounded-lg bg-olnatura-700 px-4 py-2 text-[13px] font-medium text-white hover:bg-olnatura-800 disabled:opacity-40"
        >
          {item.action_label || es.executiveAdvisor.analyze}
        </button>
      )}
    </article>
  )
}

export function ExecutiveAdvisorPanel({
  data,
  isLoading = false,
  error = null,
  updatedFromConversation = false,
  onAnalyze,
  disabled = false,
  compact = false,
}: ExecutiveAdvisorPanelProps) {
  if (isLoading) {
    return (
      <section className="mb-6 rounded-2xl border border-border-subtle bg-surface-subtle/40 px-4 py-5">
        <div className="animate-pulse space-y-3">
          <div className="h-4 w-40 rounded bg-surface-subtle" />
          <div className="h-3 w-full rounded bg-surface-subtle" />
          <div className="h-20 rounded-xl bg-surface-subtle" />
        </div>
      </section>
    )
  }

  if (error) {
    return (
      <section className="mb-6 rounded-2xl border border-amber-200 bg-amber-50/80 px-4 py-4">
        <p className="text-[13px] text-amber-900">{error}</p>
      </section>
    )
  }

  if (!data) {
    return (
      <section className="mb-6 rounded-2xl border border-border-subtle bg-gradient-to-br from-surface-subtle/70 to-surface-elevated/60 px-4 py-5 md:px-5">
        <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-muted-light">
          {es.executiveAdvisor.title}
        </p>
        <h2 className="mt-2 text-[18px] font-semibold text-foreground/90 md:text-[20px]">
          {es.executiveAdvisor.emptyGreeting}
        </h2>
        <p className="mt-1 text-[14px] text-muted">{es.executiveAdvisor.subtitle}</p>
      </section>
    )
  }

  const items = compact ? data.agenda.items.slice(0, 3) : data.agenda.items
  const heading = updatedFromConversation
    ? es.executiveAdvisor.greetingUpdated
    : data.agenda.greeting || es.executiveAdvisor.emptyGreeting
  const subtitle = updatedFromConversation
    ? es.executiveAdvisor.subtitleUpdated
    : es.executiveAdvisor.subtitle

  return (
    <section className="mb-6 rounded-2xl border border-border-subtle bg-gradient-to-br from-surface-subtle/70 to-surface-elevated/60 px-4 py-5 md:px-5">
      <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-muted-light">
        {es.executiveAdvisor.title}
      </p>
      <h2 className="mt-2 text-[18px] font-semibold text-foreground/90 md:text-[20px]">{heading}</h2>
      <p className="mt-1 text-[14px] text-muted">{subtitle}</p>
      {items.length > 0 && (
        <div className="mt-5 space-y-3">
          {items.map((item, index) => (
            <AgendaCard
              key={`${item.title}-${item.suggested_query}`}
              item={item}
              index={index}
              onAnalyze={onAnalyze}
              disabled={disabled}
            />
          ))}
        </div>
      )}
    </section>
  )
}
