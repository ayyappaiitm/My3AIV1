export interface User {
  id: string
  email: string
  name: string
  created_at: string
}

export interface RecipientRelationship {
  to_recipient_id: string
  relationship_type: string
  is_bidirectional: boolean
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
  street_address?: string
  city?: string
  state_province?: string
  postal_code?: string
  country?: string
  address_validation_status?: 'validated' | 'unvalidated' | 'failed'
  created_at: string
  updated_at: string
  upcoming_occasions_count?: number
  is_core_contact?: boolean
  network_level?: number
  relationships?: RecipientRelationship[]
  occasions?: Occasion[]
  past_gifts?: GiftIdea[]
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
  response: string
  gift_ideas?: any[]
  requires_confirmation?: boolean
  confirmation_prompt?: string
  conversation_id: string
  metadata?: any
}

