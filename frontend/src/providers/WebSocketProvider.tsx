import { useEffect } from 'react'
import type { ReactNode } from 'react'
import { useAppDispatch, useIsConnected } from '../store/hooks'
import { connectWebSocket, disconnectWebSocket } from '../store/actions/websocketActions'
import { setConnectionError } from '../store/slices/connectionSlice'

interface WebSocketProviderProps {
  children: ReactNode
}

export const WebSocketProvider = ({ children }: WebSocketProviderProps) => {
  const dispatch = useAppDispatch()
  const isConnected = useIsConnected()

  useEffect(() => {
    // Connect when app mounts
    dispatch(connectWebSocket())

    // Cleanup on app unmount
    return () => {
      dispatch(disconnectWebSocket())
    }
  }, [dispatch])

  // Handle page visibility changes to reconnect when user returns
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden && !isConnected) {
        // Page became visible and not connected, reconnect
        console.log('Page visible, reconnecting...')
        dispatch(connectWebSocket())
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [dispatch, isConnected])

  // Handle online/offline events
  useEffect(() => {
    const handleOnline = () => {
      console.log('Network online, reconnecting...')
      dispatch(connectWebSocket())
    }

    const handleOffline = () => {
      console.log('Network offline')
      dispatch(setConnectionError('Network connection lost'))
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [dispatch])

  return <>{children}</>
}