interface SuggestedQuestionsFollowUpProps {
  questions: string[]
  onSelect: (question: string) => void
  disabled?: boolean
}

export function SuggestedQuestionsFollowUp({
  questions,
  onSelect,
  disabled = false,
}: SuggestedQuestionsFollowUpProps) {
  if (questions.length === 0) return null

  return (
    <div className="mt-5 border-t border-border-subtle pt-4">
      <p className="text-[11px] font-medium uppercase tracking-[0.14em] text-muted-light">
        También puedes consultar:
      </p>
      <ul className="mt-3 space-y-2">
        {questions.map((question) => (
          <li key={question}>
            <button
              type="button"
              disabled={disabled}
              onClick={() => onSelect(question)}
              className="transition-premium text-left text-[14px] leading-6 text-olnatura-700 hover:text-olnatura-900 disabled:opacity-40"
            >
              • {question}
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
