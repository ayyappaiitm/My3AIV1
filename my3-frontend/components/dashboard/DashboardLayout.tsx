'use client'

import { useState, useEffect } from 'react'
// import { AnimatedBackground } from './AnimatedBackground' // Commented out for deployment
import { ChatWindow } from './ChatWindow'
import { Header } from './Header'
import { ParallaxBackground } from '@/components/landing/ParallaxBackground'
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
        <ParallaxBackground>
          <div className="flex items-center justify-center h-[calc(100vh-64px)] px-2 sm:px-4">
            <div className="w-full max-w-2xl">
              <ChatWindowSkeleton />
            </div>
          </div>
        </ParallaxBackground>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen relative">
      {/* Header - Fixed at top */}
      <div className="relative z-40">
        <Header />
      </div>

      {/* Parallax Background - Behind content */}
      <div 
        className="absolute inset-0" 
        style={{ 
          top: '64px',
          width: '100%',
          height: 'calc(100vh - 64px)',
          zIndex: 0,
        }}
      >
        <ParallaxBackground>
          <div className="h-full flex items-center justify-center px-2 sm:px-4">
            {/* Frosted glass container for ChatWindow */}
            <div 
              className="relative z-30 backdrop-blur-xl bg-white/90 dark:bg-gray-900/90 rounded-3xl p-6 md:p-8 max-w-4xl w-full shadow-2xl border border-white/30"
              style={{
                backdropFilter: 'blur(24px) saturate(180%)',
                WebkitBackdropFilter: 'blur(24px) saturate(180%)',
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
              }}
            >
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
        </ParallaxBackground>
      </div>
    </div>
  )
}
