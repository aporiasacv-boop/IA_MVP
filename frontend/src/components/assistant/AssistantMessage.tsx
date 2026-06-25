import { DEBUG_MODE } from '../../config/featureFlags'
import type { ChatMessage } from '../../types/chat'
import { ExecutiveResponseSummary } from './ExecutiveResponseSummary'
import { ExecutiveText } from './ExecutiveText'
import { HybridTechnicalDetails } from './HybridTechnicalDetails'
import { ResponseOriginBadge } from './ResponseOriginBadge'
import { SuggestedQuestionsFollowUp } from './SuggestedQuestionsFollowUp'
import { TechnicalDetails } from './TechnicalDetails'

interface AssistantMessageProps {
  message: ChatMessage
  onSuggestedQuestion?: (question: string) => void
  suggestionsDisabled?: boolean
  isClarificationPending?: boolean
}

function shouldHideFollowUp(message: ChatMessage, isClarificationPending: boolean): boolean {
  if (isClarificationPending) return true
  const handledBy = message.hybrid?.handledBy
  if (
    handledBy === 'slot_clarification' ||
    handledBy === 'capability_discovery' ||
    handledBy === 'guided_fallback'
  ) {
    return true
  }
  return false
}

export function AssistantMessage({
  message,
  onSuggestedQuestion,
  suggestionsDisabled = false,
  isClarificationPending = false,
}: AssistantMessageProps) {
  if (message.isError) {
    return (
      <article className="animate-fade-in-up py-5 md:py-6">
        <p className="text-[15px] leading-7 text-red-700/90 md:text-base">{message.content}</p>
      </article>
    )
  }

  const hideFollowUp = shouldHideFollowUp(message, isClarificationPending)

  return (
    <article className="animate-fade-in-up py-5 md:py-6">
      <ExecutiveResponseSummary message={message} />
      {DEBUG_MODE && <ResponseOriginBadge message={message} />}
      {isClarificationPending && message.hybrid?.handledBy === 'slot_clarification' && (
        <p className="mb-2 text-[11px] font-medium text-amber-800/90">Modo aclaración activo</p>
      )}
      <ExecutiveText content={message.content} />
      {!hideFollowUp &&
        message.suggestedQuestions &&
        message.suggestedQuestions.length > 0 &&
        onSuggestedQuestion && (
          <SuggestedQuestionsFollowUp
            questions={message.suggestedQuestions}
            onSelect={onSuggestedQuestion}
            disabled={suggestionsDisabled}
          />
        )}
      {DEBUG_MODE && message.hybrid && <HybridTechnicalDetails message={message} />}
      <TechnicalDetails message={message} />
    </article>
  )
}
