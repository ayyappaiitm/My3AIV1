'use client'

import { useState, useCallback } from 'react'
import { apiClient } from '@/lib/api/client'
import { Message, ChatRequest, ChatResponse } from '@/lib/types'

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const sendMessage = useCallback(
    async (content: string) => {
      // Add user message immediately
      const userMessage: Message = {
        id: Date.now().toString(),
        role: 'user',
        content,
      }
      setMessages((prev) => [...prev, userMessage])
      setIsLoading(true)

      try {
        const request: ChatRequest = {
          message: content,
          conversation_id: conversationId || undefined,
        }

        const response = await apiClient.post<ChatResponse>('/api/chat', request)

        // Update conversation ID
        if (response.data.conversation_id) {
          setConversationId(response.data.conversation_id)
        }

        // Add assistant message
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: response.data.message.content,
          metadata: response.data.state,
        }
        setMessages((prev) => [...prev, assistantMessage])
      } catch (error) {
        console.error('Chat error:', error)
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
        }
        setMessages((prev) => [...prev, errorMessage])
      } finally {
        setIsLoading(false)
      }
    },
    [conversationId]
  )

  return {
    messages,
    sendMessage,
    isLoading,
  }
}

