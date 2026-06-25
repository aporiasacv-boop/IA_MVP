import { useCallback, useState } from 'react'
import { LOADING_MESSAGES } from '../constants/suggestions'
import {
  isHybridChatResult,
  mapApiResponseToMessage,
  mapHybridChatResultToMessage,
  sendChatQuestion,
} from '../services/chatApi'
import { chatSessionManager } from '../services/chatSessionManager'
import { recordChatResponse, recordHybridResponse } from '../services/performanceStore'
import { ChatApiError } from '../types/chat'
import type { ChatMessage, RecentQuery } from '../types/chat'

let messageCounter = 0
let queryCounter = 0

function nextId(prefix: string): string {
  messageCounter += 1
  return `${prefix}-${messageCounter}`
}

function pickLoadingMessage(): string {
  const index = Math.floor(Math.random() * LOADING_MESSAGES.length)
  return LOADING_MESSAGES[index] ?? LOADING_MESSAGES[0]
}

export function useChatApi() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [recentQueries, setRecentQueries] = useState<RecentQuery[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [loadingMessage, setLoadingMessage] = useState(LOADING_MESSAGES[0])
  const [error, setError] = useState<string | null>(null)
  const [isClarificationPending, setIsClarificationPending] = useState(
    () => chatSessionManager.isPendingClarification(),
  )

  const refreshClarificationState = useCallback(() => {
    setIsClarificationPending(chatSessionManager.isPendingClarification())
  }, [])

  const startNewConversation = useCallback(() => {
    chatSessionManager.startNewConversation()
    setMessages([])
    setRecentQueries([])
    setError(null)
    refreshClarificationState()
  }, [refreshClarificationState])

  const submitQuestion = useCallback(async (question: string) => {
    const trimmed = question.trim()
    if (!trimmed || isLoading) return

    setError(null)
    setLoadingMessage(pickLoadingMessage())

    const userMessage: ChatMessage = {
      id: nextId('u'),
      role: 'user',
      content: trimmed,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      const response = await sendChatQuestion(trimmed)
      if (isHybridChatResult(response)) {
        const assistantMessage = mapHybridChatResultToMessage(response, nextId('a'))
        setMessages((prev) => [...prev, assistantMessage])
        recordHybridResponse(trimmed, response)
      } else {
        const assistantMessage = mapApiResponseToMessage(response, nextId('a'))
        setMessages((prev) => [...prev, assistantMessage])
        recordChatResponse(trimmed, response)
      }

      refreshClarificationState()

      queryCounter += 1
      const entry: RecentQuery = {
        id: `rq-${queryCounter}`,
        question: trimmed,
        askedAt: new Date(),
      }
      setRecentQueries((prev) => [
        entry,
        ...prev.filter((q) => q.question !== trimmed),
      ].slice(0, 8))
    } catch (err) {
      const message =
        err instanceof ChatApiError
          ? err.message
          : 'No fue posible obtener una respuesta del sistema.'
      setError(message)
      setMessages((prev) => [
        ...prev,
        {
          id: nextId('e'),
          role: 'assistant',
          content: message,
          isError: true,
          timestamp: new Date(),
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }, [isLoading, refreshClarificationState])

  return {
    messages,
    recentQueries,
    isLoading,
    loadingMessage,
    error,
    isClarificationPending,
    submitQuestion,
    startNewConversation,
    sessionMetrics: chatSessionManager.getMetrics(),
    clarificationCompletionRate: chatSessionManager.getClarificationCompletionRate(),
    sessionId: chatSessionManager.getSessionId(),
  }
}
