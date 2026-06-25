interface RecentQueriesProps {
  queries: { id: string; question: string }[]
  onSelect: (question: string) => void
}

export function RecentQueries({ queries, onSelect }: RecentQueriesProps) {
  if (queries.length === 0) return null

  return (
    <div className="mx-auto mt-3 w-full max-w-3xl">
      <p className="mb-2 text-[10px] uppercase tracking-[0.14em] text-muted-light">
        Consultas recientes
      </p>
      <div className="flex flex-wrap gap-2">
        {queries.slice(0, 4).map((query) => (
          <button
            key={query.id}
            type="button"
            onClick={() => onSelect(query.question)}
            className="transition-premium truncate max-w-[220px] rounded-lg px-2.5 py-1 text-[11px] text-muted-light hover:bg-surface-subtle hover:text-muted"
          >
            {query.question}
          </button>
        ))}
      </div>
    </div>
  )
}
