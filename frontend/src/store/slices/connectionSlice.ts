import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface ConnectionState {
  ws: WebSocket | null
  isConnected: boolean
  isConnecting: boolean
  connectionError: string | null
  reconnectAttempts: number
  maxReconnectAttempts: number
}

const initialState: ConnectionState = {
  ws: null,
  isConnected: false,
  isConnecting: false,
  connectionError: null,
  reconnectAttempts: 0,
  maxReconnectAttempts: 5,
}

const connectionSlice = createSlice({
  name: 'connection',
  initialState,
  reducers: {
    setWebSocket: (state, action: PayloadAction<WebSocket | null>) => {
      state.ws = action.payload
    },
    
    setConnected: (state, action: PayloadAction<boolean>) => {
      state.isConnected = action.payload
      if (action.payload) {
        state.isConnecting = false
        state.reconnectAttempts = 0
        state.connectionError = null
      }
    },
    
    setConnecting: (state, action: PayloadAction<boolean>) => {
      state.isConnecting = action.payload
    },
    
    setConnectionError: (state, action: PayloadAction<string | null>) => {
      state.connectionError = action.payload
    },
    
    incrementReconnectAttempts: (state) => {
      state.reconnectAttempts += 1
    },
    
    resetReconnectAttempts: (state) => {
      state.reconnectAttempts = 0
    },
    
    disconnect: (state) => {
      if (state.ws) {
        state.ws.close(1000, 'Client disconnecting')
      }
      state.ws = null
      state.isConnected = false
      state.isConnecting = false
    },
  },
})

export const {
  setWebSocket,
  setConnected,
  setConnecting,
  setConnectionError,
  incrementReconnectAttempts,
  resetReconnectAttempts,
  disconnect,
} = connectionSlice.actions

export default connectionSlice.reducer