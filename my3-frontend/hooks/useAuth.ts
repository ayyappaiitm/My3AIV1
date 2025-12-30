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
    const loadUser = async () => {
      const token = localStorage.getItem('auth_token')
      if (token) {
        // Try to get user info from token or localStorage
        // For now, we'll check if user data is in localStorage
        // In production, you'd verify token with backend
        const storedUser = localStorage.getItem('user_data')
        if (storedUser) {
          try {
            setUser(JSON.parse(storedUser))
          } catch (e) {
            // Invalid stored data, clear it
            localStorage.removeItem('user_data')
          }
        }
      }
      setIsLoading(false)
    }
    
    loadUser()
  }, [])

  const login = async (email: string, password: string) => {
    try {
      const response = await apiClient.post<AuthResponse>('/api/auth/login', {
        email,
        password,
      })

      localStorage.setItem('auth_token', response.data.access_token)
      localStorage.setItem('user_data', JSON.stringify(response.data.user))
      setUser(response.data.user)
      return response.data
    } catch (error: any) {
      // Extract error message from API response
      const errorMessage = error.response?.data?.detail || error.message || 'Login failed'
      throw new Error(errorMessage)
    }
  }

  const register = async (name: string, email: string, password: string) => {
    try {
      const response = await apiClient.post<AuthResponse>('/api/auth/register', {
        name,
        email,
        password,
      })

      // Save token and user from registration response
      localStorage.setItem('auth_token', response.data.access_token)
      localStorage.setItem('user_data', JSON.stringify(response.data.user))
      setUser(response.data.user)
      return response.data.user
    } catch (error: any) {
      // Extract error message from API response
      const errorMessage = error.response?.data?.detail || error.message || 'Registration failed'
      throw new Error(errorMessage)
    }
  }

  const logout = () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_data')
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

