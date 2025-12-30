'use client'

import { motion } from 'framer-motion'

interface SkeletonProps {
  className?: string
  variant?: 'text' | 'circular' | 'rectangular'
  width?: string | number
  height?: string | number
  animate?: boolean
}

export function Skeleton({ 
  className = '', 
  variant = 'rectangular',
  width,
  height,
  animate = true 
}: SkeletonProps) {
  const baseClasses = 'bg-gray-200 dark:bg-gray-700 rounded'
  
  const variantClasses = {
    text: 'h-4',
    circular: 'rounded-full',
    rectangular: 'rounded',
  }
  
  const style: React.CSSProperties = {}
  if (width) style.width = typeof width === 'number' ? `${width}px` : width
  if (height) style.height = typeof height === 'number' ? `${height}px` : height
  
  return (
    <div
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
      style={style}
    >
      {animate && (
        <motion.div
          className="h-full w-full bg-gradient-to-r from-transparent via-white/20 to-transparent rounded"
          animate={{
            x: ['-100%', '100%'],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: 'linear',
          }}
        />
      )}
    </div>
  )
}

// Pre-built skeleton components
export function ChatMessageSkeleton() {
  return (
    <div className="flex gap-3 animate-pulse">
      <Skeleton variant="circular" width={40} height={40} />
      <div className="flex-1 space-y-2">
        <Skeleton variant="text" width="75%" />
        <Skeleton variant="text" width="50%" />
      </div>
    </div>
  )
}

export function ChatWindowSkeleton() {
  return (
    <div className="w-full h-[600px] bg-white/95 backdrop-blur-lg rounded-3xl shadow-lg border border-white/30 p-6 space-y-4">
      {/* Header Skeleton */}
      <div className="h-16 bg-gradient-to-r from-[#FF6B6B] to-[#FFA07A] rounded-2xl animate-pulse" />
      
      {/* Messages Skeleton */}
      <div className="space-y-4 flex-1">
        <ChatMessageSkeleton />
        <div className="flex gap-3 justify-end">
          <div className="flex-1 space-y-2 max-w-xs">
            <Skeleton variant="text" width="100%" height={16} />
            <Skeleton variant="text" width="66%" height={16} />
          </div>
          <Skeleton variant="circular" width={40} height={40} />
        </div>
        <ChatMessageSkeleton />
      </div>
      
      {/* Input Skeleton */}
      <div className="h-16 bg-gray-100 rounded-xl animate-pulse" />
    </div>
  )
}

export function DashboardSkeleton() {
  return (
    <div className="min-h-screen bg-[#FFF9F5]">
      <div className="flex items-center justify-center h-[calc(100vh-64px)]">
        <div className="w-full max-w-2xl px-4">
          <ChatWindowSkeleton />
        </div>
      </div>
    </div>
  )
}

