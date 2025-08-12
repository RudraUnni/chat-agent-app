import { AppDispatch } from '../index'
import { addMessage, updateMessage, setTyping } from '../slices/chatSlice'
import { WEBSOCKET_CONNECT, WEBSOCKET_DISCONNECT, WEBSOCKET_SEND } from '../middleware/websocketMiddleware'
import type { ChatMessage, WsMessage } from '../../types/chat'

// Action creators for WebSocket operations
export const connectWebSocket = () => ({
  type: WEBSOCKET_CONNECT
})

export const disconnectWebSocket = () => ({
  type: WEBSOCKET_DISCONNECT
})

export const sendWebSocketMessage = (message: WsMessage) => ({
  type: WEBSOCKET_SEND,
  payload: message
})

// Thunk action for sending a chat message
export const sendChatMessage = (content: string) => (dispatch: AppDispatch) => {
  if (!content.trim()) return

  // Add user message immediately
  const userMessage: ChatMessage = {
    id: Date.now().toString(),
    content: content.trim(),
    role: 'user',
    timestamp: new Date().toISOString(),
    status: 'sending'
  }
  
  dispatch(addMessage(userMessage))

  // Send via WebSocket
  const wsMessage: WsMessage = {
    type: 'message',
    content: content.trim(),
    timestamp: new Date().toISOString()
  }
  
  dispatch(sendWebSocketMessage(wsMessage))
  
  // Update message status and set typing
  dispatch(updateMessage({ 
    id: userMessage.id, 
    updates: { status: 'sent' } 
  }))
  dispatch(setTyping(true))
}