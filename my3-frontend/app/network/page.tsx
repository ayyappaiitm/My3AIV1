'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { NetworkGraph } from '@/components/dashboard/NetworkGraph'
import { Header } from '@/components/dashboard/Header'
import { useAuth } from '@/hooks/useAuth'
import { useRecipients } from '@/hooks/useRecipients'
import { ArrowLeft } from 'lucide-react'

export default function NetworkPage() {
  const { user, isLoading: authLoading } = useAuth()
  const router = useRouter()
  const { recipients, isLoading: recipientsLoading } = useRecipients(user?.id || '')

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login')
    }
  }, [user, authLoading, router])

  if (authLoading || recipientsLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#FFF9F5]">
        <div className="text-[#2D3748]">Loading...</div>
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

      {/* Back Button */}
      <Link
        href="/dashboard"
        className="absolute top-20 left-4 z-20 flex items-center space-x-2 px-4 py-2 bg-white/90 backdrop-blur-sm rounded-lg shadow-md hover:bg-white transition-colors text-sm font-medium text-gray-700"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Dashboard</span>
      </Link>

      {/* Network Graph - Full Screen */}
      <div 
        className="fixed inset-0"
        style={{ 
          top: '64px',
          left: 0,
          right: 0,
          bottom: 0,
          width: '100vw',
          height: 'calc(100vh - 64px)',
          zIndex: 0
        }}
      >
        <NetworkGraph 
          recipients={recipients || []}
          activeRecipientId={null}
          isTyping={false}
        />
      </div>
      
      {/* Debug info - remove in production */}
      {process.env.NODE_ENV === 'development' && (
        <div className="fixed bottom-4 right-4 bg-black/80 text-white text-xs p-2 rounded z-30">
          <div>Recipients: {recipients?.length || 0}</div>
          <div>User ID: {user?.id || 'none'}</div>
        </div>
      )}
    </div>
  )
}

