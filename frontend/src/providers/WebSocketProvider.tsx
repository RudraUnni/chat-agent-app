import { useEffect } from 'react'
import type { ReactNode } from 'react'
import { useChatStore } from '../store/chatStore'

interface WebSocketProviderProps {
  children: ReactNode
}

export const WebSocketProvider = ({ children }: WebSocketProviderProps) => {
  const connect = useChatStore((state) => state.connect)
  const disconnect = useChatStore((state) => state.disconnect)

  useEffect(() => {
    // Connect when app mounts
    connect().catch(console.error)

    // Cleanup on app unmount
    return () => {
      disconnect()
    }
  }, []) // Empty dependency - only run once

  // Optional: Handle page visibility changes to reconnect when user returns
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        // Page became visible, ensure connection
        const state = useChatStore.getState()
        if (!state.isConnected && !state.ws) {
          connect().catch(console.error)
        }
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [connect])

  // Optional: Handle online/offline events
  useEffect(() => {
    const handleOnline = () => {
      console.log('Network online, reconnecting...')
      connect().catch(console.error)
    }

    const handleOffline = () => {
      console.log('Network offline')
      useChatStore.getState().setError('Network connection lost')
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [connect])

  return <>{children}</>
}