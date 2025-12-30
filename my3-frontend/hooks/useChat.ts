'use client'

import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { chatAPI } from '@/lib/api/client'
import { Message } from '@/lib/types'

interface PendingConfirmation {
  conversationId: string
  prompt: string
}

export function useChat(userId: string) {
  const [messages, setMessages] = useState<Message[]>([])
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [pendingConfirmation, setPendingConfirmation] = useState<PendingConfirmation | null>(null)
  const queryClient = useQueryClient()

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: async (message: string) => {
      return chatAPI.sendMessage({
        message,
        user_id: userId,
        conversation_id: conversationId || undefined,
      })
    },
    onMutate: (message) => {
      // Optimistic update: Add user message immediately
      const userMessage: Message = {
        id: crypto.randomUUID(),
        role: 'user',
        content: message,
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, userMessage])
    },
    onSuccess: (data) => {
      // Add AI response
      const aiMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.response,
        metadata: {
          gift_ideas: data.gift_ideas,
          requires_confirmation: data.requires_confirmation,
          confirmation_prompt: data.confirmation_prompt,
          conversation_id: data.conversation_id,
          ...data.metadata,
        },
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, aiMessage])

      // Set conversation ID
      if (data.conversation_id) {
        setConversationId(data.conversation_id)
      }

      // Handle confirmation prompt
      if (data.requires_confirmation) {
        setPendingConfirmation({
          conversationId: data.conversation_id,
          prompt: data.confirmation_prompt || 'Please confirm this action',
        })
      }

      // Invalidate recipients cache (might have been added)
      queryClient.invalidateQueries({ queryKey: ['recipients', userId] })
    },
    onError: (error: any) => {
      // Extract user-friendly error message
      const errorMessage = error?.message || 'Failed to send message. Please try again.'
      
      // Show specific error toast
      if (errorMessage.includes('timeout') || errorMessage.includes('connection')) {
        toast.error('Connection issue', {
          description: 'Unable to reach the server. Please check your internet connection.',
        })
      } else if (errorMessage.includes('session') || errorMessage.includes('expired')) {
        toast.error('Session expired', {
          description: 'Please log in again to continue.',
        })
      } else {
        toast.error('Failed to send message', {
          description: errorMessage,
        })
      }
      
      console.error('Chat error:', error)
      
      // Add error message to chat
      const chatErrorMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `I'm sorry, but I encountered an error: ${errorMessage}. Please try again, or refresh the page if the problem persists.`,
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, chatErrorMessage])
    },
  })

  // Confirm action mutation
  const confirmMutation = useMutation({
    mutationFn: async (confirmed: boolean) => {
      if (!conversationId) {
        throw new Error('No conversation ID available')
      }
      return chatAPI.confirm({
        conversation_id: conversationId,
        user_id: userId,
        confirmed,
      })
    },
    onSuccess: (data) => {
      setPendingConfirmation(null)

      // Add system message
      const systemMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.message || 'Action completed successfully',
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, systemMessage])

      // Refresh recipients
      queryClient.invalidateQueries({ queryKey: ['recipients', userId] })

      toast.success(data.message || 'Action completed successfully')
    },
    onError: (error: any) => {
      const errorMessage = error?.message || 'Failed to confirm action. Please try again.'
      
      toast.error('Action failed', {
        description: errorMessage,
      })
      
      console.error('Confirm action error:', error)
    },
  })

  return {
    messages,
    sendMessage: sendMessageMutation.mutate,
    confirmAction: confirmMutation.mutate,
    isLoading: sendMessageMutation.isPending,
    pendingConfirmation,
    conversationId,
  }
}
