import { useState, useCallback } from 'react'
import type { ChatMessage } from '../../../types/chat'

interface UseChatReturn {
  messages: ChatMessage[]
  isTyping: boolean
  error: string | null
  addMessage: (message: ChatMessage) => void
  updateMessage: (messageId: string, updates: Partial<ChatMessage>) => void
  clearMessages: () => void
  setIsTyping: (typing: boolean) => void
  setError: (error: string | null) => void
  clearError: () => void
}

const useChat = (): UseChatReturn => {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isTyping, setIsTyping] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const addMessage = useCallback((message: ChatMessage) => {
    setMessages(prev => {
      // Check if message already exists (for status updates)
      const existingIndex = prev.findIndex(m => m.id === message.id)
      if (existingIndex !== -1) {
        // Update existing message
        const updated = [...prev]
        updated[existingIndex] = { ...updated[existingIndex], ...message }
        return updated
      }
      // Add new message
      return [...prev, message]
    })
  }, [])

  const updateMessage = useCallback((messageId: string, updates: Partial<ChatMessage>) => {
    setMessages(prev =>
      prev.map(message =>
        message.id === messageId ? { ...message, ...updates } : message
      )
    )
  }, [])

  const clearMessages = useCallback(() => {
    setMessages([])
  }, [])

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  return {
    messages,
    isTyping,
    error,
    addMessage,
    updateMessage,
    clearMessages,
    setIsTyping,
    setError,
    clearError,
  }
}

export default useChat