import { useState } from 'react'
import type { ChatMessage } from '../../types/chat'
import { es, translateQueryType, translateResponseMode } from '../../i18n/spanish'

interface TechnicalDetailsProps {
  message: ChatMessage
}

function formatMs(value?: number): string {
  if (value === undefined) return '—'
  return `${Math.round(value)} ms`
}

function formatMode(mode?: string): string {
  return translateResponseMode(mode)
}

function formatConfidence(value?: number): string {
  if (value === undefined) return '—'
  return `${(value * 100).toFixed(0)}%`
}

function formatSources(sources?: string[]): string {
  if (!sources?.length) return '—'
  return sources.map((s) => s.toLowerCase()).join(' · ')
}

function formatTokens(message: ChatMessage): string {
  const estimated = message.promptMetrics?.estimated_tokens
  if (estimated !== undefined) return String(estimated)
  if (message.responseMode === 'DETERMINISTIC') return '0'
  return '—'
}

export function TechnicalDetails({ message }: TechnicalDetailsProps) {
  const [open, setOpen] = useState(false)
  const timings = message.timings

  if (!timings) return null

  const nlpMs =
    timings.spell_correction_ms +
    timings.synonym_resolution_ms +
    timings.intent_normalization_ms

  const rows = [
    { label: es.chat.mode, value: formatMode(message.responseMode) },
    { label: es.chat.intent, value: translateQueryType(message.intent) },
    { label: es.chat.confidence, value: formatConfidence(message.intentConfidence) },
    { label: es.chat.totalTime, value: formatMs(timings.total_ms) },
    { label: es.chat.nlp, value: formatMs(nlpMs) },
    { label: es.chat.entityExtraction, value: formatMs(timings.entity_extraction_ms) },
    { label: es.chat.router, value: formatMs(timings.router_ms) },
    { label: es.chat.deterministicEngine, value: formatMs(timings.deterministic_ms) },
    { label: es.chat.llm, value: formatMs(timings.llm_ms) },
    { label: es.chat.tokens, value: formatTokens(message) },
    { label: es.chat.sources, value: formatSources(message.sources), full: true },
  ]

  return (
    <div className="mt-5">
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className="transition-premium text-[12px] text-muted-light hover:text-muted"
      >
        {open ? '▾' : '▸'} {es.chat.advancedInfo}
      </button>

      {open && (
        <div className="animate-fade-in-up mt-3 rounded-xl border border-border-subtle bg-surface-subtle/70 px-4 py-4">
          <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {rows.map((row) => (
              <div key={row.label} className={row.full ? 'sm:col-span-2 lg:col-span-3' : undefined}>
                <dt className="text-[10px] uppercase tracking-[0.12em] text-muted-light">
                  {row.label}
                </dt>
                <dd className="mt-1 text-[13px] font-medium text-foreground/85">{row.value}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}
    </div>
  )
}
