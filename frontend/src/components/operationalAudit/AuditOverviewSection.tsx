import type { AuditOverview } from '../../types/operationalAudit'
import { es, getMetricTooltip } from '../../i18n/spanish'
import { AnalyticsCard } from '../analytics/AnalyticsCard'

const formatter = new Intl.NumberFormat('es-MX')

interface AuditOverviewSectionProps {
  overview: AuditOverview | null
  isLoading?: boolean
}

export function AuditOverviewSection({ overview, isLoading = false }: AuditOverviewSectionProps) {
  const cards = overview
    ? [
        {
          label: es.audit.overview.totalRequests,
          value: formatter.format(overview.total_requests),
          tooltip: getMetricTooltip('totalRequests'),
        },
        { label: es.audit.overview.successes, value: formatter.format(overview.total_successes) },
        { label: es.audit.overview.failures, value: formatter.format(overview.total_failures) },
        {
          label: `${es.audit.overview.businessPipeline} %`,
          value: `${overview.business_pipeline_pct.toFixed(1)}%`,
        },
        {
          label: `${es.audit.overview.memory} %`,
          value: `${overview.memory_pct.toFixed(1)}%`,
        },
        {
          label: `${es.audit.overview.clarification} %`,
          value: `${overview.clarification_pct.toFixed(1)}%`,
        },
        {
          label: `${es.audit.overview.capability} %`,
          value: `${overview.capability_pct.toFixed(1)}%`,
        },
        {
          label: `${es.audit.overview.guidedFallback} %`,
          value: `${overview.fallback_pct.toFixed(1)}%`,
        },
        {
          label: `${es.audit.overview.legacy} %`,
          value: `${overview.legacy_pct.toFixed(1)}%`,
        },
        {
          label: es.audit.overview.coverageScore,
          value: `${overview.coverage_score.toFixed(1)}`,
          sub: es.common.scaleZeroHundred,
          tooltip: getMetricTooltip('coverageScore'),
        },
        {
          label: es.audit.overview.coverageGapScore,
          value: `${overview.coverage_gap_score.toFixed(1)}`,
          sub: es.common.assistedAndGeneral,
          tooltip: getMetricTooltip('coverageGapScore'),
        },
      ]
    : []

  return (
    <section>
      <h2 className="text-lg font-semibold text-foreground">{es.audit.overview.title}</h2>
      <p className="mt-1 text-[13px] text-muted">{es.audit.overview.subtitle}</p>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {isLoading && !overview
          ? Array.from({ length: 6 }).map((_, index) => (
              <div
                key={index}
                className="animate-pulse rounded-2xl border border-border-subtle bg-surface-elevated px-4 py-5"
              >
                <div className="h-3 w-24 rounded bg-surface-subtle" />
                <div className="mt-4 h-8 w-16 rounded bg-surface-subtle" />
              </div>
            ))
          : cards.map((card) => <AnalyticsCard key={card.label} {...card} />)}
      </div>
    </section>
  )
}
