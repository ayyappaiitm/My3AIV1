import axios from 'axios'

// Determine API URL based on environment
const getApiUrl = () => {
  // In production, use the environment variable or default to production URL
  if (typeof window !== 'undefined') {
    // Client-side: use environment variable
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  }
  // Server-side: prefer production URL if available
  return process.env.NEXT_PUBLIC_API_URL || process.env.API_URL || 'http://localhost:8000'
}

const API_URL = getApiUrl()

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds timeout for production
  // Retry configuration will be handled by interceptors
})

// Add auth token to requests
apiClient.interceptors.request.use(
  (config) => {
    // Only access localStorage on client-side
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Enhanced error handling interceptor with retry logic
apiClient.interceptors.response.use(
  (response) => {
    // Log successful requests in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`API ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status}`)
    }
    return response
  },
  async (error) => {
    const originalRequest = error.config

    // Retry logic for network errors and 5xx errors
    if (
      !originalRequest._retry &&
      (!error.response || (error.response?.status >= 500 && error.response?.status < 600))
    ) {
      originalRequest._retry = true
      originalRequest._retryCount = (originalRequest._retryCount || 0) + 1

      // Only retry up to 2 times
      if (originalRequest._retryCount <= 2) {
        // Exponential backoff: wait 1s, then 2s
        const delay = originalRequest._retryCount * 1000
        await new Promise((resolve) => setTimeout(resolve, delay))
        return apiClient(originalRequest)
      }
    }

    // Handle authentication errors
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token')
        localStorage.removeItem('user_data')
        window.location.href = '/login'
      }
      return Promise.reject(new Error('Your session has expired. Please log in again.'))
    }

    // Handle network errors (no response from server)
    if (!error.response) {
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        return Promise.reject(new Error('Request timed out. Please check your connection and try again.'))
      }
      if (error.message === 'Network Error' || error.code === 'ERR_NETWORK') {
        return Promise.reject(
          new Error('Unable to connect to the server. Please check your internet connection.')
        )
      }
      return Promise.reject(new Error('Network error. Please try again later.'))
    }

    // Handle specific HTTP status codes
    const status = error.response?.status
    const data = error.response?.data

    switch (status) {
      case 400:
        return Promise.reject(new Error(data?.detail || 'Invalid request. Please check your input and try again.'))
      case 403:
        return Promise.reject(new Error("You don't have permission to perform this action."))
      case 404:
        return Promise.reject(new Error('The requested resource was not found.'))
      case 409:
        return Promise.reject(new Error(data?.detail || 'This resource already exists.'))
      case 422:
        return Promise.reject(new Error(data?.detail || 'Validation error. Please check your input.'))
      case 429:
        return Promise.reject(new Error('Too many requests. Please wait a moment and try again.'))
      case 500:
        return Promise.reject(new Error('Server error. Please try again later.'))
      case 503:
        return Promise.reject(new Error('Service temporarily unavailable. Please try again later.'))
      default:
        return Promise.reject(new Error(data?.detail || `An error occurred (${status}). Please try again.`))
    }
  }
)

// Chat API
export const chatAPI = {
  sendMessage: async (data: {
    message: string
    user_id: string
    conversation_id?: string
  }) => {
    const response = await apiClient.post('/api/chat', data)
    return response.data
  },

  confirm: async (data: {
    conversation_id: string
    user_id: string
    confirmed: boolean
  }) => {
    const response = await apiClient.post('/api/chat/confirm', data)
    return response.data
  },
}

// Recipients API
export const recipientAPI = {
  list: async (userId: string) => {
    const response = await apiClient.get(`/api/recipients?user_id=${userId}`)
    return response.data
  },

  get: async (id: string) => {
    const response = await apiClient.get(`/api/recipients/${id}`)
    return response.data
  },

  update: async (id: string, data: any) => {
    const response = await apiClient.put(`/api/recipients/${id}`, data)
    return response.data
  },

  delete: async (id: string) => {
    const response = await apiClient.delete(`/api/recipients/${id}`)
    return response.data
  },
}

// Auth API
export const authAPI = {
  register: async (data: {
    email: string
    password: string
    name: string
  }) => {
    const response = await apiClient.post('/api/auth/register', data)
    return response.data
  },

  login: async (data: {
    email: string
    password: string
  }) => {
    const response = await apiClient.post('/api/auth/login', data)
    return response.data
  },
}

