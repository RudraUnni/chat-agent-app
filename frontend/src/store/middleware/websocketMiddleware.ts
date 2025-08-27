import { Middleware } from '@reduxjs/toolkit'
import type { RootState } from '../index'
import { 
  setWebSocket, 
  setConnected, 
  setConnecting,
  setConnectionError,
  incrementReconnectAttempts,
} from '../slices/connectionSlice'
import { handleIncomingMessage } from '../slices/chatSlice'
import type { WsMessage } from '../../types/chat'
import { API_ENDPOINTS } from '../../utils/constants'

// Action types for WebSocket operations
export const WEBSOCKET_CONNECT = 'websocket/connect'
export const WEBSOCKET_DISCONNECT = 'websocket/disconnect'
export const WEBSOCKET_SEND = 'websocket/send'

const RECONNECT_DELAY_BASE = 1000

export const websocketMiddleware: Middleware<Record<string, never>, RootState> = (store) => {
  let reconnectTimeout: NodeJS.Timeout | null = null

  const clearReconnectTimeout = () => {
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout)
      reconnectTimeout = null
    }
  }

  const connect = () => {
    const state = store.getState()
    
    // Don't create new connection if already connected or connecting
    if (state.connection.isConnected || state.connection.isConnecting) {
      console.log('WebSocket already connected or connecting')
      return
    }

    store.dispatch(setConnecting(true))
    
    // Build WebSocket URL with user_id and conversation_id if available
    let wsUrl = API_ENDPOINTS.WS_URL
    const { currentUser } = state.user
    const { currentConversationId } = state.conversation
    
    if (currentConversationId) {
      wsUrl = `${API_ENDPOINTS.WS_URL.replace('/chat', `/chat/${currentConversationId}`)}`
    }
    
    if (currentUser) {
      const separator = wsUrl.includes('?') ? '&' : '?'
      wsUrl += `${separator}user_id=${currentUser.id}`
    }
    
    console.log('Connecting to WebSocket:', wsUrl)
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log('✅ WebSocket connected')
      store.dispatch(setWebSocket(ws))
      store.dispatch(setConnected(true))
    }

    ws.onmessage = (event) => {
      try {
        const data: WsMessage = JSON.parse(event.data)
        
        // Log system messages but don't process them as chat messages
        if (data.type === 'system') {
          console.log('System message:', data.content)
          return
        }
        
        // Handle all other message types
        store.dispatch(handleIncomingMessage({
          type: data.type,
          content: data.content,
          timestampMs: typeof data.timestamp === 'string' ? Date.parse(data.timestamp) : undefined,
          isStreamChunk: data.type === 'stream_chunk' || data.type === 'assistant_chunk'
        }))
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err)
        store.dispatch(setConnectionError('Failed to parse server message'))
      }
    }

    ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason)
      store.dispatch(setWebSocket(null))
      store.dispatch(setConnected(false))
      
      const state = store.getState()
      
      // Auto-reconnect logic
      if (event.code !== 1000 && state.connection.reconnectAttempts < state.connection.maxReconnectAttempts) {
        const delay = RECONNECT_DELAY_BASE * Math.pow(2, state.connection.reconnectAttempts)
        console.log(`Reconnecting in ${delay}ms... (${state.connection.reconnectAttempts + 1}/${state.connection.maxReconnectAttempts})`)
        
        store.dispatch(incrementReconnectAttempts())
        
        reconnectTimeout = setTimeout(() => {
          connect()
        }, delay)
      } else if (state.connection.reconnectAttempts >= state.connection.maxReconnectAttempts) {
        store.dispatch(setConnectionError('Connection lost. Please refresh the page.'))
      }
    }

    ws.onerror = (event) => {
      console.error('WebSocket error:', event)
      store.dispatch(setConnectionError('Connection error occurred'))
      store.dispatch(setConnecting(false))
    }
  }

  return (next) => (action: { type: string; payload?: unknown }) => {
    // Handle WebSocket-specific actions
    switch (action.type) {
      case WEBSOCKET_CONNECT:
        clearReconnectTimeout()
        connect()
        break

      case WEBSOCKET_DISCONNECT: {
        clearReconnectTimeout()
        const state = store.getState()
        if (state.connection.ws) {
          state.connection.ws.close(1000, 'Client disconnecting')
          store.dispatch(setWebSocket(null))
          store.dispatch(setConnected(false))
        }
        break
      }

      case WEBSOCKET_SEND: {
        console.log('🚀 WEBSOCKET_SEND action triggered with payload:', action.payload)
        const currentState = store.getState()
        console.log('🔍 WebSocket state:', {
          exists: !!currentState.connection.ws,
          readyState: currentState.connection.ws?.readyState,
          isOpen: currentState.connection.ws?.readyState === WebSocket.OPEN
        })
        if (currentState.connection.ws && currentState.connection.ws.readyState === WebSocket.OPEN) {
          const messageToSend = JSON.stringify(action.payload)
          console.log('📤 Sending WebSocket message:', messageToSend)
          currentState.connection.ws.send(messageToSend)
          console.log('✅ WebSocket message sent successfully')
        } else {
          console.error('❌ WebSocket not connected - cannot send message')
          store.dispatch(setConnectionError('Cannot send message: Not connected'))
        }
        break
      }
    }

    // Pass action to next middleware/reducer
    return next(action)
  }
}