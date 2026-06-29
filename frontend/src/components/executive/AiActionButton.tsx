import { useLocation } from 'react-router-dom'
import { useEnterpriseExperience } from '../../enterpriseExperience'
import type { AiActionIntent } from '../../enterpriseExperience'
import { es } from '../../i18n/spanish'

interface AiActionButtonProps {
  question: string
  intent?: AiActionIntent
  compact?: boolean
  label?: string
}

export function AiActionButton({
  question,
  intent = 'analyze',
  compact = false,
  label,
}: AiActionButtonProps) {
  const { navigateToAi } = useEnterpriseExperience()
  const location = useLocation()

  const text =
    label ?? (intent === 'explain' ? es.experience.explainWithAi : es.executive.analyzeWithAi)

  return (
    <button
      type="button"
      onClick={() =>
        navigateToAi(question, {
          origin: location.pathname,
          intent,
          deepLink: true,
        })
      }
      className={[
        'transition-premium inline-flex items-center gap-2 rounded-lg font-medium text-olnatura-700',
        'border border-olnatura-200/80 bg-olnatura-50 hover:bg-olnatura-100',
        compact ? 'px-3 py-1.5 text-[11px]' : 'px-4 py-2 text-[12px]',
      ].join(' ')}
    >
      <span className="inline-flex h-1.5 w-1.5 rounded-full bg-olnatura-lime" aria-hidden />
      {text}
    </button>
  )
}
