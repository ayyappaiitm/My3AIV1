'use client'

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api/client'
import { Recipient } from '@/lib/types'

export function useRecipients() {
  const { data: recipients, isLoading, error } = useQuery<Recipient[]>({
    queryKey: ['recipients'],
    queryFn: async () => {
      const response = await apiClient.get<Recipient[]>('/api/recipients')
      return response.data
    },
  })

  return {
    recipients: recipients || [],
    isLoading,
    error,
  }
}

