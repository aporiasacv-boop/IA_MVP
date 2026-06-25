import type { OntologyAssignmentItem, OntologyEntityView } from '../../types/businessOntology'
import { es } from '../../i18n/spanish'

const CATEGORY_LABELS: Record<string, string> = {
  identity: 'Identidad',
  role: 'Rol',
  nature: 'Naturaleza',
  behavior: 'Comportamiento',
}

interface ListProps {
  items: OntologyEntityView[]
  selectedId?: number
  isLoading: boolean
  onSelect: (item: OntologyEntityView) => void
}

export function OntologyEntityList({ items, selectedId, isLoading, onSelect }: ListProps) {
  return (
    <section>
      <h2 className="text-[13px] font-semibold">{es.businessOntology.list.title}</h2>
      <div className="mt-4 overflow-x-auto rounded-xl border border-border-subtle">
        <table className="min-w-full text-left text-[12px]">
          <thead className="border-b border-border-subtle bg-surface-elevated text-muted">
            <tr>
              <th className="px-3 py-2">{es.businessOntology.table.entity}</th>
              <th className="px-3 py-2">{es.businessOntology.table.movements}</th>
              <th className="px-3 py-2">{es.businessOntology.table.suggestions}</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={3} className="px-3 py-6 text-center text-muted">{es.common.loading}</td>
              </tr>
            ) : items.length === 0 ? (
              <tr>
                <td colSpan={3} className="px-3 py-6 text-center text-muted">{es.common.noData}</td>
              </tr>
            ) : (
              items.map((item) => (
                <tr
                  key={item.identity.canonical_id}
                  onClick={() => onSelect(item)}
                  className={`cursor-pointer border-b border-border-subtle/60 hover:bg-surface-elevated/60 ${
                    selectedId === item.identity.canonical_id ? 'bg-surface-elevated' : ''
                  }`}
                >
                  <td className="px-3 py-2 font-medium">{item.identity.canonical_name}</td>
                  <td className="px-3 py-2 tabular-nums">{item.profile_summary?.total_movements ?? 0}</td>
                  <td className="px-3 py-2 tabular-nums">{item.assignments.length}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  )
}

interface DetailProps {
  entity: OntologyEntityView | null
}

export function OntologyDetailPanel({ entity }: DetailProps) {
  if (!entity) {
    return <p className="text-[12px] text-muted">{es.businessOntology.detail.empty}</p>
  }

  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-[13px] font-semibold">{es.businessOntology.detail.title}</h2>
        <p className="mt-1 text-lg font-semibold">{entity.identity.canonical_name}</p>
        <p className="text-[12px] text-muted">
          {entity.identity.normalized_name}
          {entity.identity.primary_rfc ? ` · RFC ${entity.identity.primary_rfc}` : ''}
        </p>
      </div>

      {entity.profile_summary && (
        <div className="grid gap-2 sm:grid-cols-2 text-[12px]">
          <p>{es.businessOntology.detail.movements}: {entity.profile_summary.total_movements}</p>
          <p>{es.businessOntology.detail.dimensions}: {entity.profile_summary.dimensions_used.join(', ') || '—'}</p>
        </div>
      )}

      <SuggestionTable suggestions={entity.top_suggestions} />
    </section>
  )
}

function SuggestionTable({ suggestions }: { suggestions: OntologyAssignmentItem[] }) {
  return (
    <div>
      <h3 className="text-[12px] font-semibold">{es.businessOntology.detail.suggestions}</h3>
      <div className="mt-2 overflow-x-auto rounded-lg border border-border-subtle">
        <table className="min-w-full text-left text-[11px]">
          <thead className="bg-surface-elevated text-muted">
            <tr>
              <th className="px-2 py-1.5">{es.businessOntology.table.category}</th>
              <th className="px-2 py-1.5">{es.businessOntology.table.classification}</th>
              <th className="px-2 py-1.5">{es.businessOntology.table.rule}</th>
              <th className="px-2 py-1.5">{es.businessOntology.table.score}</th>
              <th className="px-2 py-1.5">{es.businessOntology.table.status}</th>
            </tr>
          </thead>
          <tbody>
            {suggestions.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-2 py-4 text-center text-muted">{es.common.noData}</td>
              </tr>
            ) : (
              suggestions.map((s) => (
                <tr key={s.assignment_id} className="border-t border-border-subtle/50">
                  <td className="px-2 py-1.5">{CATEGORY_LABELS[s.concept_category] ?? s.concept_category}</td>
                  <td className="px-2 py-1.5">{s.type_label}</td>
                  <td className="px-2 py-1.5 font-mono text-[10px]">{s.rule_code}</td>
                  <td className="px-2 py-1.5 tabular-nums">{(s.confidence * 100).toFixed(0)}%</td>
                  <td className="px-2 py-1.5">{s.status}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      {suggestions[0]?.evidence_json && (
        <pre className="mt-3 max-h-40 overflow-auto rounded-lg bg-surface-elevated p-2 text-[10px] text-muted">
          {JSON.stringify(suggestions[0].evidence_json, null, 2)}
        </pre>
      )}
    </div>
  )
}
