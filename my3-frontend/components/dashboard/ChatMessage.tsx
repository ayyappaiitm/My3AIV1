'use client'

import { useState } from 'react'
import { format } from 'date-fns'
import { motion } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import { ConfirmationPrompt } from './ConfirmationPrompt'
import { GiftCarousel } from './GiftCarousel'
import { Message } from '@/lib/types'

interface ChatMessageProps {
  message: Message
  onConfirm?: () => void
  onCancel?: () => void
}

export function ChatMessage({ message, onConfirm, onCancel }: ChatMessageProps) {
  const [showTimestamp, setShowTimestamp] = useState(false)
  const isUser = message.role === 'user'
  const requiresConfirmation = message.metadata?.requires_confirmation
  const confirmationPrompt = message.metadata?.confirmation_prompt
  const giftIdeas = message.metadata?.gift_ideas

  // Format timestamp
  const timestamp = message.created_at 
    ? format(new Date(message.created_at), 'h:mm a')
    : null

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} group`}
      onMouseEnter={() => setShowTimestamp(true)}
      onMouseLeave={() => setShowTimestamp(false)}
    >
      <div className="flex items-end gap-2 max-w-[80%]">
        {/* Avatar for assistant */}
        {!isUser && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.1, type: 'spring', stiffness: 200 }}
            className="w-8 h-8 rounded-full bg-gradient-to-r from-[#FF6B6B] to-[#FFA07A] flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
          >
            M3
          </motion.div>
        )}
        
        <div className="flex flex-col">
          <motion.div
            initial={{ scale: 0.95 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.05, duration: 0.2 }}
            className={`rounded-2xl px-4 py-3 ${
              isUser
                ? 'bg-gradient-to-r from-[#FF6B6B] to-[#FFA07A] text-white'
                : 'bg-gray-100 text-gray-800'
            }`}
            style={{
              maxWidth: '100%',
              padding: '12px 16px', // Match requirements
              borderRadius: '16px', // Match requirements
            }}
          >
            <div className={`text-sm break-words ${
              isUser ? 'text-white' : 'text-gray-800'
            }`}>
              <ReactMarkdown
                components={{
                  // Customize markdown components for proper styling
                  p: ({ children }) => (
                    <p className={`mb-2 last:mb-0 ${isUser ? 'text-white' : 'text-gray-800'}`}>
                      {children}
                    </p>
                  ),
                  strong: ({ children }) => (
                    <strong className={`font-semibold ${isUser ? 'text-white' : 'text-gray-900'}`}>
                      {children}
                    </strong>
                  ),
                  em: ({ children }) => (
                    <em className={`italic ${isUser ? 'text-white' : 'text-gray-700'}`}>
                      {children}
                    </em>
                  ),
                  ul: ({ children }) => (
                    <ul className={`list-disc list-inside mb-2 space-y-1 ${isUser ? 'text-white' : 'text-gray-800'}`}>
                      {children}
                    </ul>
                  ),
                  ol: ({ children }) => (
                    <ol className={`list-decimal list-inside mb-2 space-y-1 ${isUser ? 'text-white' : 'text-gray-800'}`}>
                      {children}
                    </ol>
                  ),
                  li: ({ children }) => (
                    <li className="text-sm">{children}</li>
                  ),
                  code: ({ children }) => (
                    <code className={`px-1.5 py-0.5 rounded text-xs font-mono ${
                      isUser ? 'bg-white/20 text-white' : 'bg-gray-200 text-gray-800'
                    }`}>
                      {children}
                    </code>
                  ),
                  blockquote: ({ children }) => (
                    <blockquote className={`border-l-2 pl-3 my-2 ${
                      isUser ? 'border-white/30 text-white' : 'border-gray-300 text-gray-700'
                    }`}>
                      {children}
                    </blockquote>
                  ),
                  h1: ({ children }) => (
                    <h1 className={`text-lg font-bold mb-2 ${isUser ? 'text-white' : 'text-gray-900'}`}>
                      {children}
                    </h1>
                  ),
                  h2: ({ children }) => (
                    <h2 className={`text-base font-bold mb-2 ${isUser ? 'text-white' : 'text-gray-900'}`}>
                      {children}
                    </h2>
                  ),
                  h3: ({ children }) => (
                    <h3 className={`text-sm font-semibold mb-1 ${isUser ? 'text-white' : 'text-gray-900'}`}>
                      {children}
                    </h3>
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          </motion.div>
          
          {/* Timestamp on hover */}
          {timestamp && showTimestamp && (
            <motion.span
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className={`text-xs text-gray-400 mt-1 ${isUser ? 'text-right' : 'text-left'}`}
            >
              {timestamp}
            </motion.span>
          )}
        </div>

        {/* Avatar for user */}
        {isUser && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.1, type: 'spring', stiffness: 200 }}
            className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center text-gray-600 text-xs font-bold flex-shrink-0"
          >
            You
          </motion.div>
        )}
      </div>
      
      {/* Gift ideas as carousel (if any) */}
      {!isUser && giftIdeas && giftIdeas.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.3 }}
          className="mt-4 max-w-full"
        >
          <GiftCarousel
            gifts={giftIdeas}
            recipientName={message.metadata?.recipient_name}
            onCategoryLike={(category) => {
              // TODO: Implement category like feedback - can be used for future recommendations
              console.log('Category liked:', category)
            }}
          />
        </motion.div>
      )}
      
      {/* Show confirmation prompt if needed */}
      {!isUser && requiresConfirmation && confirmationPrompt && onConfirm && onCancel && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.3 }}
          className="mt-2 max-w-[80%]"
        >
          <ConfirmationPrompt
            message={confirmationPrompt}
            onConfirm={onConfirm}
            onCancel={onCancel}
          />
        </motion.div>
      )}
    </motion.div>
  )
}

