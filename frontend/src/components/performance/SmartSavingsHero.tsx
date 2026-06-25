import type { SavingsExample } from '../../types/performance'
import { es, formatProcessingUnits } from '../../i18n/spanish'

interface SmartSavingsHeroProps {
  example: SavingsExample | null
  isLoading?: boolean
}

function formatTime(ms: number): string {
  if (ms >= 1000) return `~${(ms / 1000).toFixed(1)} s`
  return `${Math.round(ms)} ms`
}

export function SmartSavingsHero({ example, isLoading = false }: SmartSavingsHeroProps) {
  if (isLoading && !example) {
    return (
      <section className="px-4 pb-8 md:px-8 md:pb-10">
        <div className="animate-pulse overflow-hidden rounded-2xl border border-olnatura-200 bg-gradient-to-br from-olnatura-50 via-surface-elevated to-surface-elevated px-5 py-8 md:px-8 md:py-10">
          <div className="h-7 w-48 rounded bg-surface-subtle" />
          <div className="mt-3 h-4 w-72 rounded bg-surface-subtle" />
          <div className="mt-8 h-40 rounded-xl bg-surface-subtle" />
        </div>
      </section>
    )
  }

  if (!example) return null

  return (
    <section className="px-4 pb-8 md:px-8 md:pb-10">
      <div className="overflow-hidden rounded-2xl border border-olnatura-200 bg-gradient-to-br from-olnatura-50 via-surface-elevated to-surface-elevated px-5 py-8 shadow-[var(--shadow-soft)] md:px-8 md:py-10">
        <h2 className="text-xl font-semibold tracking-[-0.02em] text-foreground md:text-2xl">
          {es.performance.smartSavingsTitle}
        </h2>
        <p className="mt-2 text-[14px] text-muted md:text-[15px]">
          {es.performance.smartSavingsSubtitle}
        </p>

        <div className="mt-8 rounded-xl border border-border-subtle bg-surface-elevated/90 p-5 md:p-6">
          <p className="text-[14px] text-muted">
            {es.performance.questionLabel}:{' '}
            <span className="font-medium text-foreground">{example.question}</span>
          </p>

          <div className="mt-6 grid gap-3 sm:grid-cols-3">
            <StatBlock
              label={es.performance.traditionalArchitecture}
              value={formatProcessingUnits(example.traditionalTokens)}
            />
            <StatBlock
              label={es.performance.olnaturaArchitecture}
              value={formatProcessingUnits(example.actualTokens)}
              highlight
            />
            <StatBlock label={es.performance.savings} value={`${example.savingsPercent}%`} accent />
          </div>

          <div className="mt-6 grid gap-3 border-t border-border-subtle pt-6 sm:grid-cols-2">
            <StatBlock
              label={es.performance.estimatedTraditionalTime}
              value={formatTime(example.traditionalTimeMs)}
            />
            <StatBlock
              label={es.performance.actualOlnaturaTime}
              value={formatTime(example.actualTimeMs)}
              highlight
            />
          </div>
        </div>
      </div>
    </section>
  )
}

function StatBlock({
  label,
  value,
  highlight = false,
  accent = false,
}: {
  label: string
  value: string
  highlight?: boolean
  accent?: boolean
}) {
  return (
    <div
      className={[
        'rounded-xl px-4 py-4',
        accent
          ? 'bg-olnatura-600 text-white'
          : highlight
            ? 'border border-olnatura-200 bg-olnatura-50'
            : 'bg-surface-subtle',
      ].join(' ')}
    >
      <p
        className={[
          'text-[10px] uppercase tracking-[0.12em]',
          accent ? 'text-olnatura-100' : 'text-muted-light',
        ].join(' ')}
      >
        {label}
      </p>
      <p
        className={[
          'mt-2 text-xl font-semibold tracking-[-0.02em]',
          highlight && !accent ? 'text-olnatura-700' : '',
        ].join(' ')}
      >
        {value}
      </p>
    </div>
  )
}
