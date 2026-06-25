import { ConversationView } from '../components/assistant/ConversationView'
import { ChatInput } from '../components/assistant/ChatInput'
import { ChatSessionDebugPanel } from '../components/assistant/ChatSessionDebugPanel'
import { EmptyState } from '../components/assistant/EmptyState'
import { QuickSuggestions } from '../components/assistant/QuickSuggestions'
import { RecentQueries } from '../components/assistant/RecentQueries'
import { SUGGESTION_GROUPS } from '../constants/suggestions'
import { useChatApi } from '../hooks/useChatApi'
import { useScrollToBottom } from '../hooks/useScrollToBottom'

export function AssistantPage() {
  const {
    messages,
    recentQueries,
    isLoading,
    loadingMessage,
    isClarificationPending,
    submitQuestion,
    sessionId,
    clarificationCompletionRate,
  } = useChatApi()
  const scrollRef = useScrollToBottom([messages, isLoading, loadingMessage])
  const isEmpty = messages.length === 0 && !isLoading

  const lastAssistant = [...messages].reverse().find((m) => m.role === 'assistant' && !m.isError)
  const lastClarificationResolved = lastAssistant?.hybrid?.clarificationResolved

  return (
    <div className="flex h-full min-h-0 flex-col">
      <div ref={scrollRef} className="min-h-0 flex-1 overflow-y-auto">
        <div className="mx-auto w-full max-w-3xl px-4 md:max-w-4xl md:px-6">
          <ChatSessionDebugPanel
            sessionId={sessionId}
            isClarificationPending={isClarificationPending}
            clarificationCompletionRate={clarificationCompletionRate}
            lastClarificationResolved={lastClarificationResolved}
          />
          {isEmpty ? (
            <EmptyState />
          ) : (
            <div className="py-4 md:py-6">
              <ConversationView
                messages={messages}
                isLoading={isLoading}
                loadingMessage={loadingMessage}
                onSuggestedQuestion={submitQuestion}
                suggestionsDisabled={isLoading || isClarificationPending}
                isClarificationPending={isClarificationPending}
              />
            </div>
          )}
        </div>
      </div>

      <div className="shrink-0 border-t border-border-subtle bg-surface-elevated/95 px-4 py-4 backdrop-blur-sm md:px-6">
        <ChatInput onSend={submitQuestion} submitDisabled={isLoading} />
        {!isClarificationPending && (isEmpty || messages.length < 3) && (
          <QuickSuggestions
            groups={SUGGESTION_GROUPS}
            onSelect={submitQuestion}
            disabled={isLoading}
          />
        )}
        {!isClarificationPending && !isEmpty && (
          <RecentQueries
            queries={recentQueries.map((q) => ({ id: q.id, question: q.question }))}
            onSelect={submitQuestion}
          />
        )}
      </div>
    </div>
  )
}
