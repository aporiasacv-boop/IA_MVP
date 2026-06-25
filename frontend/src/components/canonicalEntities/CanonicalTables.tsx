import type { CanonicalEntityItem, CanonicalSuggestionItem } from '../../types/canonicalEntities'
import { es } from '../../i18n/spanish'

export function CanonicalEntitiesTable({
  items,
  isLoading,
}: {
  items: CanonicalEntityItem[]
  isLoading: boolean
}) {
  return (
    <section>
      <h2 className="text-[15px] font-semibold">{es.canonicalEntities.canonical.title}</h2>
      <div className="mt-4 overflow-x-auto rounded-xl border border-border-subtle">
        <table className="min-w-full text-left text-[12px]">
          <thead className="bg-surface-subtle text-muted">
            <tr>
              <th className="px-3 py-2">{es.canonicalEntities.table.name}</th>
              <th className="px-3 py-2">{es.canonicalEntities.table.rfc}</th>
              <th className="px-3 py-2">{es.canonicalEntities.table.aliases}</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && items.length === 0 ? (
              <tr><td colSpan={3} className="px-3 py-6 text-center text-muted">{es.common.loading}</td></tr>
            ) : items.length === 0 ? (
              <tr><td colSpan={3} className="px-3 py-6 text-center text-muted">{es.common.noData}</td></tr>
            ) : (
              items.map((item) => (
                <tr key={item.canonical_id} className="border-t border-border-subtle align-top">
                  <td className="px-3 py-2">
                    <p className="font-medium">{item.canonical_name}</p>
                    <p className="text-[11px] text-muted">{item.normalized_name}</p>
                  </td>
                  <td className="px-3 py-2 font-mono text-[11px]">{item.primary_rfc ?? '—'}</td>
                  <td className="px-3 py-2">
                    <ul className="space-y-1">
                      {item.aliases.map((alias) => (
                        <li key={alias.entity_id} className="text-[11px] text-muted">
                          <span className="font-mono text-foreground">{alias.entity_code}</span> · {alias.entity_name}
                          <span className="ml-1 text-muted-light">({alias.source_column})</span>
                        </li>
                      ))}
                    </ul>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  )
}

export function CanonicalSuggestionsTable({
  items,
  isLoading,
}: {
  items: CanonicalSuggestionItem[]
  isLoading: boolean
}) {
  return (
    <section>
      <h2 className="text-[15px] font-semibold">{es.canonicalEntities.suggestions.title}</h2>
      <p className="mt-1 text-[12px] text-muted">{es.canonicalEntities.suggestions.subtitle}</p>
      <div className="mt-4 overflow-x-auto rounded-xl border border-border-subtle">
        <table className="min-w-full text-left text-[12px]">
          <thead className="bg-surface-subtle text-muted">
            <tr>
              <th className="px-3 py-2">{es.canonicalEntities.suggestions.source}</th>
              <th className="px-3 py-2">{es.canonicalEntities.suggestions.candidate}</th>
              <th className="px-3 py-2">{es.canonicalEntities.suggestions.rule}</th>
              <th className="px-3 py-2">{es.canonicalEntities.suggestions.score}</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && items.length === 0 ? (
              <tr><td colSpan={4} className="px-3 py-6 text-center text-muted">{es.common.loading}</td></tr>
            ) : items.length === 0 ? (
              <tr><td colSpan={4} className="px-3 py-6 text-center text-muted">{es.common.noData}</td></tr>
            ) : (
              items.map((item) => (
                <tr key={item.suggestion_id} className="border-t border-border-subtle">
                  <td className="px-3 py-2">
                    <p className="font-mono text-[11px]">{item.source_entity.entity_code}</p>
                    <p className="truncate text-[11px] text-muted">{item.source_entity.entity_name}</p>
                  </td>
                  <td className="px-3 py-2">
                    <p className="font-mono text-[11px]">{item.candidate_entity.entity_code}</p>
                    <p className="truncate text-[11px] text-muted">{item.candidate_entity.entity_name}</p>
                  </td>
                  <td className="px-3 py-2 text-[11px]">{item.rule_used}</td>
                  <td className="px-3 py-2 tabular-nums">{(Number(item.score) * 100).toFixed(1)}%</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  )
}
