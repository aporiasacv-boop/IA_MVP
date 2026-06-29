import type { ReactNode } from 'react'

import type { ChatMessage, ExecutiveInsight } from '../../types/chat'
import { es } from '../../i18n/spanish'

interface ExecutiveInsightPanelProps {
  message: ChatMessage
}

function readInsight(metadata: Record<string, unknown> | undefined): ExecutiveInsight | null {
  const preferV2 = metadata?.insight_source === 'executive_reasoning_v2'
  const raw = preferV2
    ? metadata?.executive_insight
    : metadata?.executive_insight ?? metadata?.executive_reasoning_v2
  if (!raw || typeof raw !== 'object') return null

  const payload = raw as Record<string, unknown>
  const executiveSummary =
    typeof payload.executive_summary === 'string' ? payload.executive_summary.trim() : ''
  const businessInterpretation =
    typeof payload.business_interpretation === 'string'
      ? payload.business_interpretation.trim()
      : typeof payload.interpretation === 'string'
        ? payload.interpretation.trim()
        : ''
  const findings = Array.isArray(payload.findings)
    ? payload.findings.filter((item): item is string => typeof item === 'string' && item.trim().length > 0)
    : []
  const possibleRisks = Array.isArray(payload.possible_risks)
    ? payload.possible_risks.filter((item): item is string => typeof item === 'string' && item.trim().length > 0)
    : Array.isArray(payload.risks)
      ? payload.risks.filter((item): item is string => typeof item === 'string' && item.trim().length > 0)
      : []
  const opportunities = Array.isArray(payload.opportunities)
    ? payload.opportunities.filter(
        (item): item is string => typeof item === 'string' && item.trim().length > 0,
      )
    : []
  const recommendations = Array.isArray(payload.recommendations)
    ? payload.recommendations.filter(
        (item): item is string => typeof item === 'string' && item.trim().length > 0,
      )
    : []
  const limitations = Array.isArray(payload.limitations)
    ? payload.limitations.filter(
        (item): item is string => typeof item === 'string' && item.trim().length > 0,
      )
    : []
  const nextAnalyses = Array.isArray(payload.next_analyses)
    ? payload.next_analyses.filter(
        (item): item is string => typeof item === 'string' && item.trim().length > 0,
      )
    : []

  if (
    !executiveSummary &&
    !businessInterpretation &&
    findings.length === 0 &&
    possibleRisks.length === 0 &&
    opportunities.length === 0 &&
    recommendations.length === 0 &&
    limitations.length === 0 &&
    nextAnalyses.length === 0
  ) {
    return null
  }

  return {
    executiveSummary: executiveSummary || undefined,
    businessInterpretation: businessInterpretation || undefined,
    findings,
    possibleRisks,
    opportunities,
    recommendations,
    limitations,
    nextAnalyses,
  }
}

function InsightBlock({
  title,
  children,
}: {
  title: string
  children: ReactNode
}) {
  return (
    <section className="space-y-1.5">
      <h3 className="text-[11px] font-semibold uppercase tracking-[0.12em] text-muted-light">
        {title}
      </h3>
      <div className="text-[14px] leading-6 text-foreground/90">{children}</div>
    </section>
  )
}

export function ExecutiveInsightPanel({ message }: ExecutiveInsightPanelProps) {
  const insight = readInsight(message.hybrid?.rawMetadata)
  if (!insight) return null

  return (
    <div className="mt-5 rounded-xl border border-border-subtle bg-surface-subtle/40 px-4 py-4">
      <h2 className="text-[12px] font-semibold uppercase tracking-[0.14em] text-foreground/80">
        {es.executiveInsight.title}
      </h2>
      <div className="mt-4 space-y-4">
        {insight.executiveSummary && (
          <InsightBlock title={es.executiveInsight.executiveSummary}>
            <p>{insight.executiveSummary}</p>
          </InsightBlock>
        )}
        {insight.findings && insight.findings.length > 0 && (
          <InsightBlock title={es.executiveInsight.findings}>
            <ul className="list-disc space-y-1 pl-5">
              {insight.findings.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </InsightBlock>
        )}
        {insight.businessInterpretation && (
          <InsightBlock title={es.executiveInsight.interpretation}>
            <p>{insight.businessInterpretation}</p>
          </InsightBlock>
        )}
        {insight.possibleRisks.length > 0 && (
          <InsightBlock title={es.executiveInsight.risks}>
            <ul className="list-disc space-y-1 pl-5">
              {insight.possibleRisks.map((risk) => (
                <li key={risk}>{risk}</li>
              ))}
            </ul>
          </InsightBlock>
        )}
        {insight.opportunities && insight.opportunities.length > 0 && (
          <InsightBlock title={es.executiveInsight.opportunities}>
            <ul className="list-disc space-y-1 pl-5">
              {insight.opportunities.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </InsightBlock>
        )}
        {insight.recommendations.length > 0 && (
          <InsightBlock title={es.executiveInsight.recommendations}>
            <ul className="list-disc space-y-1 pl-5">
              {insight.recommendations.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </InsightBlock>
        )}
        {insight.limitations && insight.limitations.length > 0 && (
          <InsightBlock title={es.executiveInsight.limitations}>
            <ul className="list-disc space-y-1 pl-5">
              {insight.limitations.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </InsightBlock>
        )}
        {insight.nextAnalyses && insight.nextAnalyses.length > 0 && (
          <InsightBlock title={es.executiveInsight.nextAnalyses}>
            <ul className="list-disc space-y-1 pl-5">
              {insight.nextAnalyses.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </InsightBlock>
        )}
      </div>
    </div>
  )
}
