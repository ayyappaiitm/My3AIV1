'use client'

import { useState, KeyboardEvent, useEffect, useRef } from 'react'
import TextareaAutosize from 'react-textarea-autosize'
import { Send } from 'lucide-react'

interface ChatInputProps {
  onSend: (message: string) => void | Promise<void>
  disabled?: boolean
  preFillMessage?: string
}

export function ChatInput({ onSend, disabled, preFillMessage }: ChatInputProps) {
  const [input, setInput] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Handle pre-fill message
  useEffect(() => {
    if (preFillMessage) {
      setInput(preFillMessage)
      // Focus and select text after a brief delay to ensure DOM is ready
      setTimeout(() => {
        if (textareaRef.current) {
          textareaRef.current.focus()
          textareaRef.current.select()
        }
      }, 100)
    }
  }, [preFillMessage])

  // Auto-focus on mount
  useEffect(() => {
    if (textareaRef.current && !preFillMessage) {
      textareaRef.current.focus()
    }
  }, [])

  const handleSend = async () => {
    if (input.trim() && !disabled) {
      const message = input.trim()
      setInput('')
      await onSend(message)
      // Refocus after sending
      setTimeout(() => {
        textareaRef.current?.focus()
      }, 100)
    }
  }

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="p-3 sm:p-4 bg-white/50">
      <div className="flex gap-2 items-end">
        <TextareaAutosize
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Type your message..."
          disabled={disabled}
          minRows={1}
          maxRows={6}
          className="flex-1 px-3 sm:px-4 py-2 sm:py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#FF6B6B] focus:border-transparent resize-none disabled:opacity-50 disabled:cursor-not-allowed outline-none transition-all text-sm sm:text-base"
          style={{
            fontSize: '14px',
            lineHeight: '1.5',
          }}
        />
        <button
          onClick={handleSend}
          disabled={disabled || !input.trim()}
          className="px-3 sm:px-4 py-2 sm:py-2.5 bg-gradient-to-r from-[#FF6B6B] to-[#FFA07A] text-white rounded-lg font-medium hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity flex items-center gap-1 sm:gap-2 shadow-sm touch-manipulation"
          aria-label="Send message"
        >
          <Send size={18} className="sm:w-5 sm:h-5" />
          <span className="hidden sm:inline">Send</span>
        </button>
      </div>
      <p className="text-xs text-gray-400 mt-1 ml-1 hidden sm:block">
        Press Enter to send, Shift+Enter for new line
      </p>
    </div>
  )
}

