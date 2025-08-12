import { io } from 'socket.io-client'
import type { Socket } from 'socket.io-client'
import type { WsMessage } from '../types/chat'

class WebSocketClient {
  private socket: Socket | null = null
  private url: string
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5

  constructor(url: string = 'ws://localhost:8000') {
    this.url = url
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.socket = io(this.url, {
          transports: ['websocket'],
          timeout: 10000,
        })

        this.socket.on('connect', () => {
          console.log('Connected to WebSocket server')
          this.reconnectAttempts = 0
          resolve()
        })

        this.socket.on('connect_error', (error) => {
          console.error('WebSocket connection error:', error)
          reject(error)
        })

        this.socket.on('disconnect', (reason) => {
          console.log('Disconnected from WebSocket server:', reason)
          if (reason === 'io server disconnect') {
            // Server disconnected, attempt to reconnect
            this.handleReconnect()
          }
        })

      } catch (error) {
        reject(error)
      }
    })
  }

  private handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
      
      setTimeout(() => {
        this.connect().catch(console.error)
      }, 2000 * this.reconnectAttempts)
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }

  sendMessage(message: WsMessage) {
    if (this.socket?.connected) {
      this.socket.emit('message', message)
    } else {
      console.error('WebSocket not connected')
      throw new Error('WebSocket not connected')
    }
  }

  onMessage(callback: (message: WsMessage) => void) {
    if (this.socket) {
      this.socket.on('message', callback)
    }
  }

  onTyping(callback: (isTyping: boolean) => void) {
    if (this.socket) {
      this.socket.on('typing', callback)
    }
  }

  onError(callback: (error: string) => void) {
    if (this.socket) {
      this.socket.on('error', callback)
    }
  }

  isConnected(): boolean {
    return this.socket?.connected ?? false
  }
}

export const wsClient = new WebSocketClient()
export default WebSocketClient