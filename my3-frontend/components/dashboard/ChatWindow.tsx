'use client'

import { useState, useEffect, useRef } from 'react'
import { ChatMessage } from './ChatMessage'
import { ChatInput } from './ChatInput'
import { useChat } from '@/hooks/useChat'
import { useRecipients } from '@/hooks/useRecipients'

interface ChatWindowProps {
  onRecipientsUpdate: (recipients: any[]) => void
}

export function ChatWindow({ onRecipientsUpdate }: ChatWindowProps) {
  const { messages, sendMessage, isLoading } = useChat()
  const { recipients } = useRecipients()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    onRecipientsUpdate(recipients || [])
  }, [recipients, onRecipientsUpdate])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="w-full max-w-2xl bg-white rounded-lg shadow-2xl border border-gray-200 flex flex-col h-[600px]">
      {/* Chat Header */}
      <div className="p-4 border-b border-gray-200 bg-gradient-primary text-white rounded-t-lg">
        <h2 className="text-xl font-semibold">My3 Assistant</h2>
        <p className="text-sm opacity-90">Your personal gift concierge</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-text-light py-8">
            <p className="text-lg mb-2">👋 Hello! I'm My3.</p>
            <p>How can I help you today?</p>
          </div>
        )}
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
        {isLoading && (
          <div className="flex items-center space-x-2 text-text-light">
            <div className="w-2 h-2 bg-accent rounded-full animate-bounce" />
            <div className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
            <div className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput onSend={sendMessage} disabled={isLoading} />
    </div>
  )
}

