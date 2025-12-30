'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChatMessage } from './ChatMessage'
import { ChatInput } from './ChatInput'
import { useChat } from '@/hooks/useChat'
import { useRecipients } from '@/hooks/useRecipients'
import { Message } from '@/lib/types'

interface ChatWindowProps {
  onRecipientsUpdate?: (recipients: any[]) => void
  preFillMessage?: string
  isLoading?: boolean
  pendingConfirmation?: any
  messages?: Message[]
  onSendMessage?: (message: string) => Promise<void> | void
  onConfirm?: (confirmed: boolean) => void
}

export function ChatWindow({ 
  onRecipientsUpdate,
  preFillMessage,
  isLoading: externalIsLoading,
  pendingConfirmation,
  messages: externalMessages,
  onSendMessage: externalOnSendMessage,
  onConfirm: externalOnConfirm
}: ChatWindowProps) {
  // Note: Internal hooks require userId, but ChatWindow is typically used with external props
  // If used standalone, userId would need to be passed as a prop
  // For now, using empty string as fallback (will fail gracefully)
  const internalChat = useChat('')
  const { recipients } = useRecipients('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const messagesContainerRef = useRef<HTMLDivElement>(null)

  // Use external props if provided, otherwise use internal hooks
  const messages = externalMessages || internalChat.messages
  const sendMessage = externalOnSendMessage || internalChat.sendMessage
  const isLoading = externalIsLoading !== undefined ? externalIsLoading : internalChat.isLoading

  useEffect(() => {
    if (onRecipientsUpdate) {
      onRecipientsUpdate(recipients || [])
    }
  }, [recipients, onRecipientsUpdate])

  // Auto-scroll to bottom on new message
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  const handleSend = async (message: string) => {
    if (sendMessage) {
      await sendMessage(message)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className="w-[calc(100%-20px)] max-w-[calc(100%-20px)] h-[calc(100vh-100px)] max-h-[600px]
                 sm:w-[calc(100%-40px)] sm:max-w-[calc(100%-40px)] sm:h-[70vh]
                 md:w-[600px] md:max-w-[600px] md:h-[600px] md:max-h-[600px]
                 lg:w-[600px] lg:max-w-[600px] lg:h-[700px] lg:max-h-none
                 flex flex-col mx-auto"
      style={{
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(20px)',
        borderRadius: '16px',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
        border: '1px solid rgba(255, 255, 255, 0.3)',
      }}
    >
      {/* Chat Header */}
      <div className="p-3 sm:p-4 border-b border-gray-200/50 bg-gradient-to-r from-[#FF6B6B] to-[#FFA07A] text-white rounded-t-[16px] sm:rounded-t-3xl">
        <h2 className="text-lg sm:text-xl font-semibold">Chat with My3</h2>
        <p className="text-xs sm:text-sm opacity-90">Your personal gift concierge</p>
      </div>

      {/* Messages Area */}
      <div 
        ref={messagesContainerRef}
        className="flex-1 overflow-y-auto p-3 sm:p-4 space-y-3 sm:space-y-4"
        style={{
          scrollBehavior: 'smooth',
        }}
      >
        {messages.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center text-gray-500 py-12"
          >
            <p className="text-lg mb-2">👋 Hello! I'm My3.</p>
            <p className="text-sm">How can I help you today?</p>
            <p className="text-xs mt-2 text-gray-400">Try: "My mom loves gardening"</p>
          </motion.div>
        )}
        
        <AnimatePresence>
          {messages.map((message) => {
            const requiresConfirmation = message.metadata?.requires_confirmation
            const lastMessageWithConfirmation = messages
              .slice()
              .reverse()
              .find(m => m.metadata?.requires_confirmation)
            
            // Only show confirmation on the most recent message that requires it
            const showConfirmation = requiresConfirmation && 
              lastMessageWithConfirmation?.id === message.id &&
              pendingConfirmation
            
            return (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                <ChatMessage 
                  message={message}
                  onConfirm={showConfirmation ? () => {
                    if (externalOnConfirm) {
                      externalOnConfirm(true)
                    } else if (internalChat.confirmAction) {
                      internalChat.confirmAction(true)
                    } else if (externalOnSendMessage) {
                      externalOnSendMessage('yes')
                    }
                  } : undefined}
                  onCancel={showConfirmation ? () => {
                    if (externalOnConfirm) {
                      externalOnConfirm(false)
                    } else if (internalChat.confirmAction) {
                      internalChat.confirmAction(false)
                    } else if (externalOnSendMessage) {
                      externalOnSendMessage('no')
                    }
                  } : undefined}
                />
              </motion.div>
            )
          })}
        </AnimatePresence>

        {/* Loading indicator */}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center space-x-2 text-gray-500 py-2"
          >
            <span className="text-sm">My3 is typing</span>
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-[#FF6B6B] rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
              <div className="w-2 h-2 bg-[#FF6B6B] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              <div className="w-2 h-2 bg-[#FF6B6B] rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
            </div>
          </motion.div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Section */}
      <div className="border-t border-gray-200/50">
        <ChatInput 
          onSend={handleSend} 
          disabled={isLoading} 
          preFillMessage={preFillMessage} 
        />
      </div>
    </motion.div>
  )
}

