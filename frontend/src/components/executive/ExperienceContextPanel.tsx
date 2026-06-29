import { useEnterpriseExperience } from '../../enterpriseExperience'
import { es } from '../../i18n/spanish'

interface ExperienceContextPanelProps {
  onSelectQuestion: (question: string) => void
  showPinned?: boolean
}

export function ExperienceContextPanel({
  onSelectQuestion,
  showPinned = true,
}: ExperienceContextPanelProps) {
  const {
    context,
    pinnedQueries,
    recentQueries,
    contextualSuggestions,
    togglePin,
    isPinned,
    navigateToScreen,
  } = useEnterpriseExperience()

  const hasContent =
    pinnedQueries.length > 0 ||
    recentQueries.length > 0 ||
    contextualSuggestions.length > 0 ||
    context.lastQuery

  if (!hasContent) return null

  return (
    <aside className="mt-6 space-y-5 rounded-2xl border border-border-subtle bg-surface-elevated/60 p-4">
      <div className="flex flex-wrap gap-2">
        <QuickNavButton
          label={es.nav.executiveDashboard}
          onClick={() =>
            navigateToScreen('executive_dashboard', context.period ? { period: context.period } : {})
          }
        />
        <QuickNavButton
          label={es.nav.financialSimulator}
          onClick={() =>
            navigateToScreen(
              'financial_simulator',
              context.scenario ? { scenario: context.scenario } : {},
            )
          }
        />
      </div>

      {context.lastQuery && (
        <Section title={es.experience.continueConversation}>
          <QueryChip question={context.lastQuery} onSelect={onSelectQuestion} />
        </Section>
      )}

      {showPinned && pinnedQueries.length > 0 && (
        <Section title={es.experience.pinnedQueries}>
          {pinnedQueries.map((item) => (
            <QueryChip
              key={item.id}
              question={item.question}
              onSelect={onSelectQuestion}
              pinned
              onTogglePin={() => togglePin(item.question)}
            />
          ))}
        </Section>
      )}

      {recentQueries.length > 0 && (
        <Section title={es.experience.recentQueries}>
          {recentQueries.slice(0, 5).map((item) => (
            <QueryChip
              key={item.id}
              question={item.question}
              onSelect={onSelectQuestion}
              pinned={isPinned(item.question)}
              onTogglePin={() => togglePin(item.question)}
            />
          ))}
        </Section>
      )}

      {contextualSuggestions.length > 0 && (
        <Section title={es.experience.suggestedForContext}>
          {contextualSuggestions.map((question) => (
            <QueryChip key={question} question={question} onSelect={onSelectQuestion} />
          ))}
        </Section>
      )}
    </aside>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-muted-light">
        {title}
      </p>
      <div className="mt-2 flex flex-col gap-1.5">{children}</div>
    </div>
  )
}

function QueryChip({
  question,
  onSelect,
  pinned = false,
  onTogglePin,
}: {
  question: string
  onSelect: (q: string) => void
  pinned?: boolean
  onTogglePin?: () => void
}) {
  return (
    <div className="flex items-center gap-2">
      <button
        type="button"
        onClick={() => onSelect(question)}
        className="flex-1 rounded-lg border border-border-subtle bg-surface px-3 py-2 text-left text-[12px] text-foreground/90 hover:border-olnatura-200 hover:bg-olnatura-50/50"
      >
        {question}
      </button>
      {onTogglePin && (
        <button
          type="button"
          onClick={onTogglePin}
          aria-label={pinned ? es.experience.unpin : es.experience.pin}
          className="shrink-0 rounded-lg px-2 py-2 text-[14px] text-muted hover:text-olnatura-700"
        >
          {pinned ? '★' : '☆'}
        </button>
      )}
    </div>
  )
}

function QuickNavButton({ label, onClick }: { label: string; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="rounded-lg border border-border-subtle bg-surface px-3 py-1.5 text-[11px] font-medium text-muted hover:text-foreground"
    >
      {label}
    </button>
  )
}
