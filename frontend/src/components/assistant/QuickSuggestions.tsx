import type { SuggestionGroup } from '../../constants/suggestions'

interface QuickSuggestionsProps {
  groups: SuggestionGroup[]
  onSelect: (question: string) => void
  disabled?: boolean
}

export function QuickSuggestions({
  groups,
  onSelect,
  disabled = false,
}: QuickSuggestionsProps) {
  return (
    <div className="mx-auto mt-3 w-full max-w-3xl space-y-3">
      {groups.map((group) => (
        <div key={group.label}>
          <p className="mb-2 text-center text-[10px] font-medium uppercase tracking-[0.14em] text-muted-light">
            {group.label}
          </p>
          <div className="flex flex-wrap justify-center gap-2">
            {group.items.map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                disabled={disabled}
                onClick={() => onSelect(suggestion)}
                className="transition-premium rounded-full bg-surface-subtle px-3 py-1.5 text-[12px] text-muted hover:bg-olnatura-50 hover:text-olnatura-700 disabled:opacity-40"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
