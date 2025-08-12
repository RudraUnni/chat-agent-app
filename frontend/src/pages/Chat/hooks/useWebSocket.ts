import { useState, useCallback, useRef } from 'react'
import type { WsMessage } from '../../../types/chat'

interface UseWebSocketProps {
  onMessage?: (data: WsMessage) => void
  onTyping?: (isTyping: boolean) => void
  onError?: (error: string) => void
  onConnect?: () => void
  onDisconnect?: () => void
}

interface UseWebSocketReturn {
  isConnected: boolean
  error: string | null
  connect: () => Promise<void>
  disconnect: () => void
  sendMessage: (message: WsMessage) => Promise<void>
}

const useWebSocket = ({
  onMessage,
  onTyping,
  onError,
  onConnect,
  onDisconnect,
}: UseWebSocketProps): UseWebSocketReturn => {
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const ws = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5
  const isUnmounting = useRef(false)

  const connect = useCallback(async (): Promise<void> => {
    return new Promise((resolve, reject) => {
      try {
        // Don't create a new connection if one already exists and is open/connecting
        if (ws.current && (ws.current.readyState === WebSocket.OPEN || ws.current.readyState === WebSocket.CONNECTING)) {
          console.log('WebSocket already connected or connecting')
          if (ws.current.readyState === WebSocket.OPEN) {
            resolve()
          }
          return
        }
        
        // Close existing connection if it's in a closed or closing state
        if (ws.current && (ws.current.readyState === WebSocket.CLOSING || ws.current.readyState === WebSocket.CLOSED)) {
          ws.current = null
        }

        const wsUrl = 'ws://localhost:8000/ws/chat'
        ws.current = new WebSocket(wsUrl)

        ws.current.onopen = () => {
          console.log('WebSocket connected')
          setIsConnected(true)
          setError(null)
          reconnectAttempts.current = 0
          onConnect?.()
          resolve()
        }

        ws.current.onmessage = (event) => {
          try {
            const data: WsMessage = JSON.parse(event.data)
            
            switch (data.type) {
              case 'message':
              case 'assistant':
                onMessage?.(data)
                break
              case 'system':
                console.log('System message:', data.content)
                break
              case 'typing':
                onTyping?.(true)
                break
              case 'error':
                onError?.(data.content ?? 'Unknown error')
                break
              default:
                console.log('Unknown message type:', data.type)
            }
          } catch (err) {
            console.error('Failed to parse WebSocket message:', err)
            onError?.('Failed to parse server message')
          }
        }

        ws.current.onclose = (event) => {
          console.log('WebSocket closed:', event.code, event.reason)
          setIsConnected(false)
          onDisconnect?.()

          // Attempt to reconnect if not a normal closure and not unmounting
          if (!isUnmounting.current && event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
            const timeout = Math.pow(2, reconnectAttempts.current) * 1000 // Exponential backoff
            console.log(`Attempting to reconnect in ${timeout}ms... (${reconnectAttempts.current + 1}/${maxReconnectAttempts})`)
            
            reconnectTimeoutRef.current = setTimeout(() => {
              reconnectAttempts.current++
              connect().catch(console.error)
            }, timeout)
          } else if (reconnectAttempts.current >= maxReconnectAttempts) {
            setError('Connection lost. Please refresh the page to reconnect.')
          }
        }

        ws.current.onerror = (event) => {
          console.error('WebSocket error:', event)
          setError('Connection error occurred')
          reject(new Error('WebSocket connection failed'))
        }

        // Timeout for connection
        setTimeout(() => {
          if (ws.current?.readyState !== WebSocket.OPEN) {
            reject(new Error('WebSocket connection timeout'))
          }
        }, 10000)

      } catch (err) {
        reject(err)
      }
    })
  }, [onMessage, onTyping, onError, onConnect, onDisconnect])

  const disconnect = useCallback(() => {
    isUnmounting.current = true
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    
    if (ws.current) {
      ws.current.close(1000, 'Client disconnecting')
      ws.current = null
    }
    
    setIsConnected(false)
  }, [])

  const sendMessage = useCallback(async (message: WsMessage): Promise<void> => {
    return new Promise((resolve, reject) => {
      if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
        reject(new Error('WebSocket not connected'))
        return
      }

      try {
        ws.current.send(JSON.stringify(message))
        resolve()
      } catch (err) {
        reject(err)
      }
    })
  }, [])

  return {
    isConnected,
    error,
    connect,
    disconnect,
    sendMessage,
  }
}

export default useWebSocket