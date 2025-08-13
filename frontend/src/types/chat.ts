export interface ChatMessage {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  status?: 'sending' | 'sent' | 'delivered' | 'error'
}

export interface ChatSession {
  id: string
  title: string
  messages: ChatMessage[]
  createdAt: Date
  updatedAt: Date
}

export interface WsMessage {
  type: 'message' | 'typing' | 'error' | 'connected' | 'disconnected' | 'system' | 'assistant'
  content?: string
  timestamp?: string
  sessionId?: string
}

export interface ChatState {
  currentSession: ChatSession | null
  messages: ChatMessage[]
  isConnected: boolean
  isTyping: boolean
  error: string | null
}