import type { CostOptimizationExample } from '../../types/performance'
import { es, formatProcessingUnits } from '../../i18n/spanish'

interface CostOptimizationSectionProps {
  examples: CostOptimizationExample[]
}

export function CostOptimizationSection({ examples }: CostOptimizationSectionProps) {
  const secondaryExamples = examples.filter(
    (example) => example.question !== '¿Qué KPIs tienes?',
  )

  if (secondaryExamples.length === 0) return null

  return (
    <section className="mx-auto max-w-4xl border-t border-border-subtle px-6 py-10 md:px-12 md:py-12">
      <p className="text-[11px] font-medium uppercase tracking-[0.16em] text-muted-light">
        {es.performance.moreExamples}
      </p>
      <h2 className="mt-3 text-lg font-medium text-foreground/90">
        {es.performance.costOptimizationTitle}
      </h2>

      <div className="mt-8 space-y-6">
        {secondaryExamples.map((example) => (
          <article
            key={example.question}
            className="transition-premium rounded-2xl border border-border-subtle bg-surface-elevated/60 px-5 py-5 hover:border-olnatura-100 md:px-6"
          >
            <p className="text-sm text-muted">{example.question}</p>

            <div className="mt-5 grid gap-3 sm:grid-cols-3">
              <MiniStat
                label={es.performance.traditional}
                value={formatProcessingUnits(example.llmTokensEstimate)}
              />
              <MiniStat
                label="Olnatura"
                value={`${example.actualTokens} ${es.performance.processingUnits}`}
                highlight
              />
              <MiniStat label={es.performance.savings} value={`${example.savingsPercent}%`} />
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}

function MiniStat({
  label,
  value,
  highlight = false,
}: {
  label: string
  value: string
  highlight?: boolean
}) {
  return (
    <div
      className={[
        'rounded-xl px-4 py-3',
        highlight ? 'bg-olnatura-50 text-olnatura-700' : 'bg-surface-subtle text-foreground/85',
      ].join(' ')}
    >
      <p className="text-[10px] uppercase tracking-[0.14em] text-muted-light">{label}</p>
      <p className="mt-1.5 text-base font-semibold">{value}</p>
    </div>
  )
}
