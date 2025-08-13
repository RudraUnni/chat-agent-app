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

// Action types for WebSocket operations
export const WEBSOCKET_CONNECT = 'websocket/connect'
export const WEBSOCKET_DISCONNECT = 'websocket/disconnect'
export const WEBSOCKET_SEND = 'websocket/send'

const RECONNECT_DELAY_BASE = 1000
const WS_URL = 'ws://localhost:8000/ws/chat'

export const websocketMiddleware: Middleware<{}, RootState> = (store) => {
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
    const ws = new WebSocket(WS_URL)

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
          timestampMs: typeof data.timestamp === 'string' ? Date.parse(data.timestamp) : undefined
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

  return (next) => (action: any) => {
    // Handle WebSocket-specific actions
    switch (action.type) {
      case WEBSOCKET_CONNECT:
        clearReconnectTimeout()
        connect()
        break

      case WEBSOCKET_DISCONNECT:
        clearReconnectTimeout()
        const state = store.getState()
        if (state.connection.ws) {
          state.connection.ws.close(1000, 'Client disconnecting')
          store.dispatch(setWebSocket(null))
          store.dispatch(setConnected(false))
        }
        break

      case WEBSOCKET_SEND:
        const currentState = store.getState()
        if (currentState.connection.ws && currentState.connection.ws.readyState === WebSocket.OPEN) {
          currentState.connection.ws.send(JSON.stringify(action.payload))
        } else {
          console.error('WebSocket not connected')
          store.dispatch(setConnectionError('Cannot send message: Not connected'))
        }
        break
    }

    // Pass action to next middleware/reducer
    return next(action)
  }
}