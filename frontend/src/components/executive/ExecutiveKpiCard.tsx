import { useEnterpriseExperience } from '../../enterpriseExperience'
import type { KpiQuestionKey } from '../../enterpriseExperience/questions'
import { buildKpiQuestion } from '../../enterpriseExperience/questions'
import { AiActionButton } from './AiActionButton'

interface ExecutiveKpiCardProps {
  label: string
  value: string
  hint?: string
  trend?: 'up' | 'down' | 'neutral'
  kpiKey?: KpiQuestionKey
  isLoading?: boolean
}

export function ExecutiveKpiCard({
  label,
  value,
  hint,
  trend = 'neutral',
  kpiKey,
  isLoading = false,
}: ExecutiveKpiCardProps) {
  const { context } = useEnterpriseExperience()
  const trendColor =
    trend === 'up'
      ? 'text-emerald-700'
      : trend === 'down'
        ? 'text-amber-700'
        : 'text-muted'

  const question = kpiKey ? buildKpiQuestion(kpiKey, context.period) : null

  return (
    <article className="executive-card flex flex-col justify-between rounded-2xl border border-border-subtle bg-surface-elevated p-5 shadow-[var(--shadow-soft)]">
      {isLoading ? (
        <div className="animate-pulse space-y-3">
          <div className="h-3 w-24 rounded bg-surface-subtle" />
          <div className="h-9 w-20 rounded bg-surface-subtle" />
          <div className="h-3 w-full rounded bg-surface-subtle" />
        </div>
      ) : (
        <>
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-light">
              {label}
            </p>
            <p className="mt-3 text-[2rem] font-semibold tabular-nums tracking-[-0.03em] text-foreground">
              {value}
            </p>
            {hint && <p className={`mt-2 text-[13px] leading-5 ${trendColor}`}>{hint}</p>}
          </div>
          {question && (
            <div className="mt-5 border-t border-border-subtle pt-4">
              <AiActionButton question={question} compact />
            </div>
          )}
        </>
      )}
    </article>
  )
}
