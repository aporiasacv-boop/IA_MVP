import { useCallback, useEffect, useState } from 'react'
import { LOADING_MESSAGES } from '../constants/suggestions'
import { enterpriseExperienceStore } from '../enterpriseExperience/store'
import type { SerializedChatMessage } from '../enterpriseExperience/types'
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
import type { HybridChatResult } from '../types/hybrid-chat'

interface UseChatApiOptions {
  onHybridResponse?: (response: HybridChatResult) => void
}

let messageCounter = 0

function nextId(prefix: string): string {
  messageCounter += 1
  return `${prefix}-${messageCounter}`
}

function pickLoadingMessage(): string {
  const index = Math.floor(Math.random() * LOADING_MESSAGES.length)
  return LOADING_MESSAGES[index] ?? LOADING_MESSAGES[0]
}

function serializeMessage(message: ChatMessage): SerializedChatMessage {
  return {
    id: message.id,
    role: message.role,
    content: message.content,
    isError: message.isError,
    timestamp: message.timestamp.toISOString(),
  }
}

function deserializeMessage(message: SerializedChatMessage): ChatMessage {
  return {
    id: message.id,
    role: message.role,
    content: message.content,
    isError: message.isError,
    timestamp: new Date(message.timestamp),
  }
}

function restoreMessages(): ChatMessage[] {
  return enterpriseExperienceStore.getSnapshot().conversation.map(deserializeMessage)
}

function restoreRecentQueries(): RecentQuery[] {
  return enterpriseExperienceStore.getSnapshot().recentQueries.map((item) => ({
    id: item.id,
    question: item.question,
    askedAt: new Date(item.askedAt),
  }))
}

export function useChatApi(options: UseChatApiOptions = {}) {
  const [messages, setMessages] = useState<ChatMessage[]>(() => restoreMessages())
  const [recentQueries, setRecentQueries] = useState<RecentQuery[]>(() => restoreRecentQueries())
  const [isLoading, setIsLoading] = useState(false)
  const [loadingMessage, setLoadingMessage] = useState(LOADING_MESSAGES[0])
  const [error, setError] = useState<string | null>(null)
  const [isClarificationPending, setIsClarificationPending] = useState(
    () => chatSessionManager.isPendingClarification(),
  )

  useEffect(() => {
    enterpriseExperienceStore.setConversation(messages.map(serializeMessage))
  }, [messages])

  const refreshClarificationState = useCallback(() => {
    setIsClarificationPending(chatSessionManager.isPendingClarification())
  }, [])

  const startNewConversation = useCallback(() => {
    chatSessionManager.startNewConversation()
    enterpriseExperienceStore.resetConversation()
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
    enterpriseExperienceStore.addRecentQuery(trimmed)

    try {
      const response = await sendChatQuestion(trimmed)
      if (isHybridChatResult(response)) {
        const assistantMessage = mapHybridChatResultToMessage(response, nextId('a'))
        setMessages((prev) => [...prev, assistantMessage])
        recordHybridResponse(trimmed, response)
        options.onHybridResponse?.(response)
      } else {
        const assistantMessage = mapApiResponseToMessage(response, nextId('a'))
        setMessages((prev) => [...prev, assistantMessage])
        recordChatResponse(trimmed, response)
      }

      refreshClarificationState()

      const stored = enterpriseExperienceStore.getSnapshot().recentQueries
      setRecentQueries(
        stored.map((item) => ({
          id: item.id,
          question: item.question,
          askedAt: new Date(item.askedAt),
        })),
      )
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
  }, [isLoading, options.onHybridResponse, refreshClarificationState])

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
