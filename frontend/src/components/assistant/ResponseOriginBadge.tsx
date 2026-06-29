import type { ChatMessage } from '../../types/chat'
import { resolveGatewayRouteLabel } from '../../i18n/spanish'

interface ResponseOriginBadgeProps {
  message: ChatMessage
}

const BADGE_STYLES: Record<string, string> = {
  conversation_gateway: 'text-violet-700/90',
  business_pipeline: 'text-emerald-700/90',
  legacy_chat: 'text-sky-700/90',
  guided_fallback: 'text-amber-700/90',
  capability_discovery: 'text-violet-700/90',
  conversation_memory: 'text-teal-700/90',
  product_identity: 'text-indigo-700/90',
  executive_reasoning: 'text-rose-700/90',
}

export function ResponseOriginBadge({ message }: ResponseOriginBadgeProps) {
  const handledBy = message.hybrid?.handledBy
  const metadata = message.hybrid?.rawMetadata

  if (!handledBy && !metadata?.gateway_decision) return null

  const label = resolveGatewayRouteLabel(metadata, handledBy)
  const style = BADGE_STYLES[handledBy ?? ''] ?? 'text-muted'

  return (
    <p className={`mb-2 text-[11px] font-medium ${style}`}>
      Ruta: {label}
    </p>
  )
}
