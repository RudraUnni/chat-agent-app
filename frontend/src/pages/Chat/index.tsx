import { useEffect } from 'react'
import MessageList from './components/MessageList'
import MessageInput from './components/MessageInput'
import TypingIndicator from './components/TypingIndicator'
import useChat from './hooks/useChat'
import useWebSocket from './hooks/useWebSocket'
import type { ChatMessage, WsMessage } from '../../types/chat'
import { AlertCircle, Wifi, WifiOff } from 'lucide-react'

const Chat = () => {
  const { 
    messages, 
    isTyping, 
    error, 
    addMessage, 
    setIsTyping, 
    setError,
    clearError 
  } = useChat()
  
  const { 
    isConnected, 
    sendMessage, 
    connect, 
    disconnect 
  } = useWebSocket({
    onMessage: (data: WsMessage) => {
      addMessage({
        id: Date.now().toString(),
        content: data.content ?? '',
        role: 'assistant',
        timestamp: new Date(),
        status: 'sent'
      })
      setIsTyping(false)
    },
    onTyping: (typing) => {
      setIsTyping(typing)
    },
    onError: (error) => {
      setError(error)
    }
  })

  useEffect(() => {
    let mounted = true
    
    const initConnection = async () => {
      if (mounted) {
        try {
          await connect()
        } catch (error) {
          console.error('Failed to connect:', error)
        }
      }
    }
    
    initConnection()
    
    return () => {
      mounted = false
      disconnect()
    }
  }, []) // Empty dependency array - only run once on mount

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || !isConnected) return

    // Add user message immediately
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: content.trim(),
      role: 'user' as const,
      timestamp: new Date(),
      status: 'sending' as const
    }
    
    addMessage(userMessage)
    clearError()

    try {
      // Send via WebSocket
      await sendMessage({ type: 'message', content: content.trim(), timestamp: new Date().toISOString() })
      
      // Update message status
      addMessage({ ...userMessage, status: 'sent' })
      setIsTyping(true)
    } catch (error) {
      console.error('Failed to send message:', error)
      setError('Failed to send message. Please try again.')
      addMessage({ ...userMessage, status: 'error' })
    }
  }

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-white">
        <h1 className="text-xl font-semibold text-gray-900">Chat Assistant</h1>
        <div className="flex items-center space-x-2">
          {isConnected ? (
            <div className="flex items-center text-green-600">
              <Wifi className="w-4 h-4 mr-1" />
              <span className="text-sm">Connected</span>
            </div>
          ) : (
            <div className="flex items-center text-red-600">
              <WifiOff className="w-4 h-4 mr-1" />
              <span className="text-sm">Disconnected</span>
            </div>
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mx-4 mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center">
          <AlertCircle className="w-5 h-5 text-red-500 mr-2 flex-shrink-0" />
          <span className="text-red-700">{error}</span>
          <button
            onClick={clearError}
            className="ml-auto text-red-500 hover:text-red-700"
          >
            ×
          </button>
        </div>
      )}

      {/* Chat Messages */}
      <div className="flex-1 overflow-hidden">
        <MessageList messages={messages} />
      </div>

      {/* Typing Indicator */}
      {isTyping && (
        <div className="px-4">
          <TypingIndicator />
        </div>
      )}

      {/* Message Input */}
      <div className="border-t bg-white">
        <MessageInput
          onSendMessage={handleSendMessage}
          disabled={!isConnected}
          placeholder={
            isConnected 
              ? "Type your message..." 
              : "Connecting..."
          }
        />
      </div>
    </div>
  )
}

export default Chat