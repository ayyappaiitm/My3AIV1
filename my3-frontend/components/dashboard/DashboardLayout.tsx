'use client'

import { useState, useEffect } from 'react'
import { NetworkGraph } from './NetworkGraph'
import { ChatWindow } from './ChatWindow'
import { useAuth } from '@/hooks/useAuth'
import { useRouter } from 'next/navigation'

export function DashboardLayout() {
  const { user, isLoading } = useAuth()
  const router = useRouter()
  const [recipients, setRecipients] = useState<any[]>([])

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login')
    }
  }, [user, isLoading, router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-text-light">Loading...</div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Network Graph Background */}
      <div className="absolute inset-0 z-0">
        <NetworkGraph recipients={recipients} />
      </div>
      
      {/* Chat Window Overlay */}
      <div className="relative z-10 flex items-center justify-center min-h-screen p-4">
        <ChatWindow onRecipientsUpdate={setRecipients} />
      </div>
    </div>
  )
}

