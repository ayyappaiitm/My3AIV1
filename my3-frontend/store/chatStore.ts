import { create } from 'zustand'
import { Message } from '@/lib/types'

interface ChatState {
  messages: Message[]
  conversationId: string | null
  addMessage: (message: Message) => void
  setConversationId: (id: string | null) => void
  clearMessages: () => void
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  conversationId: null,
  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),
  setConversationId: (id) => set({ conversationId: id }),
  clearMessages: () => set({ messages: [], conversationId: null }),
}))

