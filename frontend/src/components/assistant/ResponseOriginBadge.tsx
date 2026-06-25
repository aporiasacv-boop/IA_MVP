import type { ChatMessage } from '../../types/chat'
import { translateHandledBy } from '../../i18n/spanish'

interface ResponseOriginBadgeProps {
  message: ChatMessage
}

const BADGE_STYLES: Record<string, string> = {
  business_pipeline: 'text-emerald-700/90',
  legacy_chat: 'text-sky-700/90',
  guided_fallback: 'text-amber-700/90',
  capability_discovery: 'text-violet-700/90',
  conversation_memory: 'text-teal-700/90',
  slot_clarification: 'text-orange-700/90',
}

export function ResponseOriginBadge({ message }: ResponseOriginBadgeProps) {
  const handledBy = message.hybrid?.handledBy

  if (!handledBy) return null

  const label = translateHandledBy(handledBy)
  const style = BADGE_STYLES[handledBy] ?? 'text-muted'

  return (
    <p className={`mb-2 text-[11px] font-medium ${style}`}>
      Canal: {label}
    </p>
  )
}
