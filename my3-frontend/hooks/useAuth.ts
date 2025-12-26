'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api/client'
import { User } from '@/lib/types'

interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      // Verify token and get user info
      // For now, we'll just check if token exists
      // In production, you'd verify with backend
      setIsLoading(false)
    } else {
      setIsLoading(false)
    }
  }, [])

  const login = async (email: string, password: string) => {
    const formData = new URLSearchParams()
    formData.append('email', email)
    formData.append('password', password)

    const response = await apiClient.post<AuthResponse>('/api/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })

    localStorage.setItem('auth_token', response.data.access_token)
    setUser(response.data.user)
    return response.data
  }

  const register = async (name: string, email: string, password: string) => {
    const response = await apiClient.post<User>('/api/auth/register', {
      name,
      email,
      password,
    })

    // Auto-login after registration
    await login(email, password)
    return response.data
  }

  const logout = () => {
    localStorage.removeItem('auth_token')
    setUser(null)
  }

  return {
    user,
    isLoading,
    login,
    register,
    logout,
  }
}

