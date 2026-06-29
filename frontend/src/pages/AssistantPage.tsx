import { useEffect, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import { ConversationView } from '../components/assistant/ConversationView'
import { ChatInput } from '../components/assistant/ChatInput'
import { ChatSessionDebugPanel } from '../components/assistant/ChatSessionDebugPanel'
import { EmptyState } from '../components/assistant/EmptyState'
import { QuickSuggestions } from '../components/assistant/QuickSuggestions'
import { RecentQueries } from '../components/assistant/RecentQueries'
import { ExecutiveAdvisorPanel } from '../components/executive/ExecutiveAdvisorPanel'
import { EnterpriseShell } from '../components/executive/EnterpriseShell'
import { ExperienceContextPanel } from '../components/executive/ExperienceContextPanel'
import { SUGGESTION_GROUPS } from '../constants/suggestions'
import { useEnterpriseExperience } from '../enterpriseExperience'
import { useChatApi } from '../hooks/useChatApi'
import { useExecutiveAdvisor } from '../hooks/useExecutiveAdvisor'
import { useScrollToBottom } from '../hooks/useScrollToBottom'
import { es } from '../i18n/spanish'

export function AssistantPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const pendingQueryRef = useRef<string | null>(null)
  const { contextualSuggestions, syncFromSearchParams, context } = useEnterpriseExperience()
  const advisor = useExecutiveAdvisor({
    period: context.period,
    scenario: context.scenario,
  })

  const {
    messages,
    recentQueries,
    isLoading,
    loadingMessage,
    isClarificationPending,
    submitQuestion,
    sessionId,
    clarificationCompletionRate,
  } = useChatApi({
    onHybridResponse: (response) => advisor.applyFromHybridMetadata(response.metadata ?? {}),
  })

  const scrollRef = useScrollToBottom([messages, isLoading, loadingMessage])
  const isEmpty = messages.length === 0 && !isLoading

  const lastAssistant = [...messages].reverse().find((m) => m.role === 'assistant' && !m.isError)
  const lastClarificationResolved = lastAssistant?.hybrid?.clarificationResolved

  useEffect(() => {
    syncFromSearchParams(searchParams)
  }, [searchParams, syncFromSearchParams])

  useEffect(() => {
    const q = searchParams.get('q')?.trim()
    if (!q || pendingQueryRef.current === q) return
    pendingQueryRef.current = q
    setSearchParams({}, { replace: true })
    void submitQuestion(q)
  }, [searchParams, setSearchParams, submitQuestion])

  const suggestionGroups =
    contextualSuggestions.length > 0
      ? [{ label: es.experience.suggestedForContext, items: contextualSuggestions }]
      : SUGGESTION_GROUPS

  return (
    <EnterpriseShell
      screen="enterprise_ai"
      title={es.executive.ai.title}
      subtitle={isEmpty ? es.executive.ai.emptySubtitle : es.executive.ai.contextHint}
      fullBleed
      footer={
        <div className="shrink-0 border-t border-border-subtle bg-surface-elevated/95 px-4 py-4 backdrop-blur-sm md:px-6">
          <ChatInput onSend={submitQuestion} submitDisabled={isLoading} />
          {!isClarificationPending && (isEmpty || messages.length < 3) && (
            <QuickSuggestions
              groups={suggestionGroups}
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
      }
    >
      <div ref={scrollRef} className="mx-auto w-full max-w-4xl px-4 md:px-6">
        <ExecutiveAdvisorPanel
          data={advisor.data}
          isLoading={advisor.isLoading}
          error={advisor.error}
          updatedFromConversation={advisor.updatedFromConversation}
          onAnalyze={submitQuestion}
          disabled={isLoading || isClarificationPending}
        />
        <ChatSessionDebugPanel
          sessionId={sessionId}
          isClarificationPending={isClarificationPending}
          clarificationCompletionRate={clarificationCompletionRate}
          lastClarificationResolved={lastClarificationResolved}
        />
        {isEmpty ? (
          <div className="py-6">
            <EmptyState />
            <ExperienceContextPanel onSelectQuestion={submitQuestion} />
          </div>
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
            <ExperienceContextPanel onSelectQuestion={submitQuestion} showPinned={false} />
          </div>
        )}
      </div>
    </EnterpriseShell>
  )
}
