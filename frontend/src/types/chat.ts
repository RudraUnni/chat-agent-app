import type { MessageStatus } from '../utils/constants'

export interface ChatMessage {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: number
  status?: MessageStatus
}

export interface ChatSession {
  id: string
  title: string
  messages: ChatMessage[]
  createdAt: number
  updatedAt: number
}

export interface WsMessage {
  type: 'message' | 'typing' | 'error' | 'connected' | 'disconnected' | 'system' | 'assistant'
  content?: string
  timestamp?: string
  sessionId?: string
}

