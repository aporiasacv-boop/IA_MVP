import type { BusinessExecutionPlan, SemanticParseResult, SemanticStatistics } from '../../types/semanticIntent'
import { es } from '../../i18n/spanish'

export function SemanticStatisticsSection({
  statistics,
  isLoading,
}: {
  statistics: SemanticStatistics | null
  isLoading: boolean
}) {
  const cards = [
    { label: es.semanticIntent.stats.parses, value: statistics?.semantic_parses ?? '—' },
    { label: es.semanticIntent.stats.plans, value: statistics?.execution_plans ?? '—' },
    {
      label: es.semanticIntent.stats.confidence,
      value: statistics ? `${(statistics.average_semantic_confidence * 100).toFixed(1)}%` : '—',
    },
    {
      label: es.semanticIntent.stats.successRate,
      value: statistics ? `${(statistics.planner_success_rate * 100).toFixed(1)}%` : '—',
    },
    { label: es.semanticIntent.stats.unknownVerbs, value: statistics?.unknown_verbs ?? '—' },
  ]

  return (
    <section>
      <h2 className="text-[13px] font-semibold">{es.semanticIntent.stats.title}</h2>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {cards.map((card) => (
          <div key={card.label} className="rounded-xl border border-border-subtle bg-surface-elevated px-4 py-3">
            <p className="text-[11px] text-muted">{card.label}</p>
            <p className="mt-1 text-xl font-semibold tabular-nums">
              {isLoading ? es.common.loading : card.value}
            </p>
          </div>
        ))}
      </div>
    </section>
  )
}

export function SemanticAnalysisPanel({
  parse,
  plan,
}: {
  parse: SemanticParseResult | null
  plan: BusinessExecutionPlan | null
}) {
  if (!parse || !plan) {
    return <p className="text-[12px] text-muted">{es.semanticIntent.detail.empty}</p>
  }

  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-[13px] font-semibold">{es.semanticIntent.detail.title}</h2>
        <p className="mt-2 text-[12px] text-muted">{parse.original_question}</p>
      </div>

      <InfoGrid
        items={[
          [es.semanticIntent.detail.verb, parse.business_verb?.verb_id ?? '—'],
          [es.semanticIntent.detail.category, parse.business_verb?.category ?? '—'],
          [es.semanticIntent.detail.confidence, `${(parseFloat(parse.confidence) * 100).toFixed(1)}%`],
          [es.semanticIntent.detail.strategy, plan.execution_strategy],
        ]}
      />

      <TagSection title={es.semanticIntent.detail.objects} tags={plan.detected_objects} />
      <TagSection title={es.semanticIntent.detail.context} tags={plan.detected_context} />
      <TagSection title={es.semanticIntent.detail.knowledge} tags={plan.required_knowledge} />
      <TagSection title={es.semanticIntent.detail.reasoning} tags={plan.required_reasoning} />
      <TagSection title={es.semanticIntent.detail.evidence} tags={plan.required_evidence} />

      {(plan.incomplete || plan.incompatible_strategy) && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-[11px] text-amber-800">
          {plan.incomplete ? es.semanticIntent.detail.incomplete : ''}
          {plan.incompatible_strategy ? ` ${es.semanticIntent.detail.incompatible}` : ''}
        </div>
      )}
    </section>
  )
}

function InfoGrid({ items }: { items: [string, string][] }) {
  return (
    <div className="grid gap-2 sm:grid-cols-2 text-[12px]">
      {items.map(([label, value]) => (
        <p key={label}>
          <span className="text-muted">{label}: </span>
          <span className="font-medium">{value}</span>
        </p>
      ))}
    </div>
  )
}

function TagSection({ title, tags }: { title: string; tags: string[] }) {
  if (tags.length === 0) return null
  return (
    <div>
      <h3 className="text-[12px] font-semibold">{title}</h3>
      <div className="mt-2 flex flex-wrap gap-2">
        {tags.map((tag) => (
          <span
            key={tag}
            className="rounded-full border border-border-subtle bg-surface-elevated px-2.5 py-1 text-[10px] font-medium"
          >
            {tag}
          </span>
        ))}
      </div>
    </div>
  )
}
