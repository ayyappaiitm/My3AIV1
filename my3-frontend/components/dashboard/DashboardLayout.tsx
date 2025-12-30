'use client'

import { useState, useEffect } from 'react'
import { AnimatedBackground } from './AnimatedBackground'
import { ChatWindow } from './ChatWindow'
import { Header } from './Header'
import { useAuth } from '@/hooks/useAuth'
import { useRecipients } from '@/hooks/useRecipients'
import { useChat } from '@/hooks/useChat'
import { useRouter } from 'next/navigation'
import { Recipient } from '@/lib/types'
import { ChatWindowSkeleton } from '@/components/ui/LoadingSkeleton'

export function DashboardLayout() {
  const { user, isLoading: authLoading } = useAuth()
  const router = useRouter()
  const { recipients, isLoading: recipientsLoading } = useRecipients(user?.id || '')
  const { messages, sendMessage, confirmAction, isLoading: chatLoading, pendingConfirmation } = useChat(user?.id || '')
  
  const [activeRecipientId, setActiveRecipientId] = useState<string | null>(null)
  const [preFillMessage, setPreFillMessage] = useState<string | undefined>(undefined)

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login')
    }
  }, [user, authLoading, router])

  // Handle node click - pre-fill chat with recipient name
  const handleNodeClick = (recipient: Recipient) => {
    setActiveRecipientId(recipient.id)
    setPreFillMessage(`Gift ideas for ${recipient.name}`)
    
    // Clear pre-fill after a delay (so it can be used)
    setTimeout(() => {
      setPreFillMessage(undefined)
    }, 100)
  }

  // Use pendingConfirmation from useChat hook instead of managing it separately
  // The hook now handles this internally

  if (authLoading || recipientsLoading) {
    return (
      <div className="min-h-screen bg-[#FFF9F5]">
        <Header />
        <div className="flex items-center justify-center h-[calc(100vh-64px)] px-2 sm:px-4">
          <div className="w-full max-w-2xl">
            <ChatWindowSkeleton />
          </div>
        </div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-[#FFF9F5] relative">
      {/* Header */}
      <Header />

      {/* Animated Background */}
      <div 
        className="absolute inset-0" 
        style={{ 
          top: '64px',
          width: '100%',
          height: 'calc(100vh - 64px)',
          zIndex: 0,
          pointerEvents: 'none' // Allow clicks to pass through to chat
        }}
      >
        <AnimatedBackground />
      </div>
      
      {/* Chat Window Overlay - Centered */}
      <div className="fixed inset-0 z-10 flex items-center justify-center pointer-events-none px-2 sm:px-4" style={{ top: '64px' }}>
        <div className="pointer-events-auto flex items-center justify-center w-full">
          <ChatWindow
            messages={messages}
            onSendMessage={sendMessage}
            onConfirm={confirmAction}
            isLoading={chatLoading}
            pendingConfirmation={pendingConfirmation}
            preFillMessage={preFillMessage}
          />
        </div>
      </div>
    </div>
  )
}
