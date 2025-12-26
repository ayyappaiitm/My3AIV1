export interface User {
  id: string
  email: string
  name: string
  created_at: string
}

export interface Recipient {
  id: string
  user_id: string
  name: string
  relationship?: string
  age_band?: string
  interests: string[]
  constraints: string[]
  notes?: string
  created_at: string
  updated_at: string
}

export interface Occasion {
  id: string
  user_id: string
  recipient_id: string
  name: string
  occasion_type?: string
  date?: string
  budget_range?: string
  status: 'idea_needed' | 'shortlisted' | 'decided' | 'done'
  created_at: string
  updated_at: string
}

export interface GiftIdea {
  id: string
  occasion_id: string
  title: string
  description?: string
  price?: string
  category?: string
  url?: string
  is_shortlisted: string
  created_at: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  metadata?: any
  created_at?: string
}

export interface ChatRequest {
  message: string
  conversation_id?: string
}

export interface ChatResponse {
  conversation_id: string
  message: Message
  state?: any
}

