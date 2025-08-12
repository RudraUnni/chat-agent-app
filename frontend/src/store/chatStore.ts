import { create } from 'zustand'
import { devtools, subscribeWithSelector } from 'zustand/middleware'
import type { ChatMessage, WsMessage } from '../types/chat'

interface ChatState {
  // Connection state
  ws: WebSocket | null
  isConnected: boolean
  connectionError: string | null
  reconnectAttempts: number
  
  // Message state
  messages: ChatMessage[]
  isTyping: boolean
  streamingMessageId: string | null
  
  // Actions
  connect: () => Promise<void>
  disconnect: () => void
  sendMessage: (content: string) => Promise<void>
  addMessage: (message: ChatMessage) => void
  updateMessage: (id: string, updates: Partial<ChatMessage>) => void
  setTyping: (isTyping: boolean) => void
  setError: (error: string | null) => void
  clearMessages: () => void
}

const MAX_RECONNECT_ATTEMPTS = 5
const RECONNECT_DELAY_BASE = 1000

export const useChatStore = create<ChatState>()(
  devtools(
    subscribeWithSelector((set, get) => ({
      // Initial state
      ws: null,
      isConnected: false,
      connectionError: null,
      reconnectAttempts: 0,
      messages: [],
      isTyping: false,
      streamingMessageId: null,

      // Connect to WebSocket
      connect: async () => {
        const state = get()
        
        // Don't create new connection if already connected
        if (state.ws?.readyState === WebSocket.OPEN || state.ws?.readyState === WebSocket.CONNECTING) {
          console.log('WebSocket already connected or connecting')
          return
        }

        return new Promise((resolve, reject) => {
          try {
            const wsUrl = 'ws://localhost:8000/ws/chat'
            const ws = new WebSocket(wsUrl)
            
            ws.onopen = () => {
              console.log('✅ WebSocket connected')
              set({ 
                ws, 
                isConnected: true, 
                connectionError: null,
                reconnectAttempts: 0 
              })
              resolve()
            }

            ws.onmessage = (event) => {
              try {
                const data: WsMessage = JSON.parse(event.data)
                const state = get()
                
                switch (data.type) {
                  case 'assistant':
                  case 'message':
                    // Add or update message
                    if (state.streamingMessageId) {
                      // Update existing streaming message
                      state.updateMessage(state.streamingMessageId, {
                        content: data.content || '',
                        status: 'sent'
                      })
                      set({ streamingMessageId: null, isTyping: false })
                    } else {
                      // Add new message
                      state.addMessage({
                        id: Date.now().toString(),
                        content: data.content || '',
                        role: 'assistant',
                        timestamp: new Date().toISOString(),
                        status: 'sent'
                      })
                      set({ isTyping: false })
                    }
                    break
                    
                  case 'system':
                    console.log('System message:', data.content)
                    break
                    
                  case 'typing':
                    set({ isTyping: true })
                    break
                    
                  case 'error':
                    set({ connectionError: data.content || 'Unknown error' })
                    break
                    
                  default:
                    console.log('Unknown message type:', data.type)
                }
              } catch (err) {
                console.error('Failed to parse WebSocket message:', err)
                set({ connectionError: 'Failed to parse server message' })
              }
            }

            ws.onclose = (event) => {
              console.log('WebSocket closed:', event.code, event.reason)
              set({ isConnected: false, ws: null })
              
              const state = get()
              
              // Auto-reconnect logic
              if (event.code !== 1000 && state.reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                const delay = RECONNECT_DELAY_BASE * Math.pow(2, state.reconnectAttempts)
                console.log(`Reconnecting in ${delay}ms... (${state.reconnectAttempts + 1}/${MAX_RECONNECT_ATTEMPTS})`)
                
                set({ reconnectAttempts: state.reconnectAttempts + 1 })
                
                setTimeout(() => {
                  get().connect().catch(console.error)
                }, delay)
              } else if (state.reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
                set({ connectionError: 'Connection lost. Please refresh the page.' })
              }
            }

            ws.onerror = (event) => {
              console.error('WebSocket error:', event)
              set({ connectionError: 'Connection error occurred' })
              reject(new Error('WebSocket connection failed'))
            }

            // Store the WebSocket instance
            set({ ws })
            
          } catch (err) {
            console.error('Failed to create WebSocket:', err)
            reject(err)
          }
        })
      },

      // Disconnect from WebSocket
      disconnect: () => {
        const { ws } = get()
        if (ws) {
          ws.close(1000, 'Client disconnecting')
          set({ ws: null, isConnected: false })
        }
      },

      // Send message via WebSocket
      sendMessage: async (content: string) => {
        const state = get()
        
        if (!state.ws || state.ws.readyState !== WebSocket.OPEN) {
          throw new Error('WebSocket not connected')
        }

        // Add user message immediately
        const userMessage: ChatMessage = {
          id: Date.now().toString(),
          content: content.trim(),
          role: 'user',
          timestamp: new Date().toISOString(),
          status: 'sending'
        }
        
        state.addMessage(userMessage)

        try {
          // Send via WebSocket
          const wsMessage: WsMessage = {
            type: 'message',
            content: content.trim(),
            timestamp: new Date().toISOString()
          }
          
          state.ws.send(JSON.stringify(wsMessage))
          
          // Update message status
          state.updateMessage(userMessage.id, { status: 'sent' })
          set({ isTyping: true, connectionError: null })
          
        } catch (error) {
          console.error('Failed to send message:', error)
          state.updateMessage(userMessage.id, { status: 'error' })
          throw error
        }
      },

      // Add a new message
      addMessage: (message: ChatMessage) => {
        set((state) => ({
          messages: [...state.messages, message]
        }))
      },

      // Update an existing message
      updateMessage: (id: string, updates: Partial<ChatMessage>) => {
        set((state) => ({
          messages: state.messages.map(msg =>
            msg.id === id ? { ...msg, ...updates } : msg
          )
        }))
      },

      // Set typing indicator
      setTyping: (isTyping: boolean) => {
        set({ isTyping })
      },

      // Set error
      setError: (error: string | null) => {
        set({ connectionError: error })
      },

      // Clear all messages
      clearMessages: () => {
        set({ messages: [], streamingMessageId: null })
      }
    })),
    {
      name: 'chat-store'
    }
  )
)

// Selector hooks for specific state slices
export const useMessages = () => useChatStore((state) => state.messages)
export const useIsConnected = () => useChatStore((state) => state.isConnected)
export const useIsTyping = () => useChatStore((state) => state.isTyping)
export const useConnectionError = () => useChatStore((state) => state.connectionError)