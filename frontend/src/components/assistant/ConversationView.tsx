import type { ChatMessage } from '../../types/chat'
import { AssistantMessage } from './AssistantMessage'
import { UserMessage } from './UserMessage'

interface ConversationViewProps {
  messages: ChatMessage[]
  isLoading?: boolean
  loadingMessage?: string
  onSuggestedQuestion?: (question: string) => void
  suggestionsDisabled?: boolean
  isClarificationPending?: boolean
}

export function ConversationView({
  messages,
  isLoading = false,
  loadingMessage = 'Analizando información...',
  onSuggestedQuestion,
  suggestionsDisabled = false,
  isClarificationPending = false,
}: ConversationViewProps) {
  return (
    <div className="space-y-1">
      {messages.map((message) =>
        message.role === 'user' ? (
          <UserMessage key={message.id} content={message.content} />
        ) : (
          <AssistantMessage
            key={message.id}
            message={message}
            onSuggestedQuestion={onSuggestedQuestion}
            suggestionsDisabled={suggestionsDisabled}
            isClarificationPending={isClarificationPending}
          />
        ),
      )}

      {isLoading && (
        <div className="animate-fade-in py-5">
          <p className="text-[14px] text-muted">{loadingMessage}</p>
          <div className="mt-3 flex gap-1.5">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-olnatura-400" />
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-olnatura-400 [animation-delay:180ms]" />
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-olnatura-400 [animation-delay:360ms]" />
          </div>
        </div>
      )}
    </div>
  )
}
