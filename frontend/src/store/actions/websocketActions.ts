import { createAsyncThunk } from '@reduxjs/toolkit'
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

// Async thunk action for sending a chat message
export const sendChatMessage = createAsyncThunk(
  'chat/sendMessage',
  async (content: string, { dispatch }) => {
    console.log('💬 sendChatMessage called with content:', content)
    if (!content.trim()) {
      console.log('❌ Empty content, not sending message')
      return
    }

    // Add user message immediately
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: content.trim(),
      role: 'user',
      timestamp: Date.now(),
      status: 'sending'
    }
    
    console.log('➕ Adding user message to chat:', userMessage)
    dispatch(addMessage(userMessage))

    // Send via WebSocket
    const wsMessage: WsMessage = {
      type: 'message',
      content: content.trim(),
      timestamp: new Date().toISOString()
    }
    
    console.log('🚀 Dispatching WebSocket message:', wsMessage)
    dispatch(sendWebSocketMessage(wsMessage))
    
    // Update message status and set typing
    dispatch(updateMessage({ 
      id: userMessage.id, 
      updates: { status: 'sent' } 
    }))
    dispatch(setTyping(true))
  }
)