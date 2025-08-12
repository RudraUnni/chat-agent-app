import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import type { ChatMessage } from '../../types/chat'

interface ChatState {
  messages: ChatMessage[]
  isTyping: boolean
  streamingMessageId: string | null
  error: string | null
}

const initialState: ChatState = {
  messages: [],
  isTyping: false,
  streamingMessageId: null,
  error: null,
}

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addMessage: (state, action: PayloadAction<ChatMessage>) => {
      state.messages.push(action.payload)
    },
    
    updateMessage: (state, action: PayloadAction<{ id: string; updates: Partial<ChatMessage> }>) => {
      const message = state.messages.find(msg => msg.id === action.payload.id)
      if (message) {
        Object.assign(message, action.payload.updates)
      }
    },
    
    deleteMessage: (state, action: PayloadAction<string>) => {
      state.messages = state.messages.filter(msg => msg.id !== action.payload)
    },
    
    clearMessages: (state) => {
      state.messages = []
      state.streamingMessageId = null
    },
    
    setTyping: (state, action: PayloadAction<boolean>) => {
      state.isTyping = action.payload
    },
    
    setStreamingMessageId: (state, action: PayloadAction<string | null>) => {
      state.streamingMessageId = action.payload
    },
    
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload
    },
    
    // Action for handling incoming WebSocket messages
    handleIncomingMessage: (state, action: PayloadAction<{ type: string; content?: string }>) => {
      const { type, content } = action.payload
      
      switch (type) {
        case 'assistant':
        case 'message':
          if (state.streamingMessageId) {
            // Update existing streaming message
            const message = state.messages.find(msg => msg.id === state.streamingMessageId)
            if (message) {
              message.content = content || ''
              message.status = 'sent'
            }
            state.streamingMessageId = null
            state.isTyping = false
          } else {
            // Add new message
            state.messages.push({
              id: Date.now().toString(),
              content: content || '',
              role: 'assistant',
              timestamp: new Date(),
              status: 'sent'
            })
            state.isTyping = false
          }
          break
          
        case 'typing':
          state.isTyping = true
          break
          
        case 'error':
          state.error = content || 'Unknown error'
          break
      }
    },
  },
})

export const {
  addMessage,
  updateMessage,
  deleteMessage,
  clearMessages,
  setTyping,
  setStreamingMessageId,
  setError,
  handleIncomingMessage,
} = chatSlice.actions

export default chatSlice.reducer