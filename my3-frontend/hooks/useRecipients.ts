'use client'

import { useQuery } from '@tanstack/react-query'
import { recipientAPI } from '@/lib/api/client'
import { Recipient } from '@/lib/types'

export function useRecipients(userId: string) {
  const { data: recipients, isLoading, error } = useQuery<Recipient[]>({
    queryKey: ['recipients', userId],
    queryFn: () => recipientAPI.list(userId),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  return {
    recipients: recipients || [],
    isLoading,
    error,
    count: recipients?.length || 0,
    hasMaxRecipients: (recipients?.length || 0) >= 10,
  }
}
