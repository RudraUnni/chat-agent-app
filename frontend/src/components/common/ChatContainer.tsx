import { useEffect, useRef } from 'react'
import { AlertCircle, Wifi, WifiOff } from 'lucide-react'
import MessageBubble from './MessageBubble'
import { 
  useAppDispatch, 
  useMessages, 
  useIsConnected, 
  useIsTyping, 
  useConnectionError 
} from '../../store/hooks'
import { sendChatMessage } from '../../store/actions/websocketActions'
import { setConnectionError } from '../../store/slices/connectionSlice'
import type { ChatMessage } from '../../types/chat'
import ChatInput from './ChatInput'
import TypingIndicator from '../../pages/Chat/components/TypingIndicator'

const ChatContainer = () => {
  const dispatch = useAppDispatch()
  const messages = useMessages()
  const isConnected = useIsConnected()
  const isTyping = useIsTyping()
  const connectionError = useConnectionError()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const handleSendMessage = (content: string) => {
    if (!content.trim() || !isConnected) return

    dispatch(sendChatMessage(content) as any)
  }

  const clearError = () => {
    dispatch(setConnectionError(null))
  }

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isTyping])

  const EmptyState = () => (
    <div className="flex-1 flex items-center justify-center p-8">
      <div className="text-center max-w-md">
        <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
          <svg
            className="w-10 h-10 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.477 8-10 8a9.863 9.863 0 01-4.906-1.289l-3.378 1.287A1.5 1.5 0 012 18.5V12c0-4.418 4.477-8 10-8s10 3.582 10 8z"
            />
          </svg>
        </div>
        <h3 className="text-2xl font-semibold text-gray-900 mb-3">
          Welcome to your Medical Assistant
        </h3>
        <p className="text-gray-600 leading-relaxed">
          Start a conversation by typing a medical question below. I can help you research 
          medical topics, find relevant studies, and provide evidence-based information from PubMed.
        </p>
      </div>
    </div>
  )

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto bg-white">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-white shadow-sm">
        <h1 className="text-xl font-semibold text-gray-900">Medical Assistant</h1>
        <div className="flex items-center space-x-2">
          {isConnected ? (
            <div className="flex items-center text-green-600">
              <Wifi className="w-4 h-4 mr-1" />
              <span className="text-sm font-medium">Connected</span>
            </div>
          ) : (
            <div className="flex items-center text-red-600">
              <WifiOff className="w-4 h-4 mr-1" />
              <span className="text-sm font-medium">Disconnected</span>
            </div>
          )}
        </div>
      </div>

      {/* Error Display */}
      {connectionError && (
        <div className="mx-4 mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center">
          <AlertCircle className="w-5 h-5 text-red-500 mr-2 flex-shrink-0" />
          <span className="text-red-700 flex-1">{connectionError}</span>
          <button
            onClick={clearError}
            className="ml-2 text-red-500 hover:text-red-700 font-bold text-lg leading-none"
          >
            ×
          </button>
        </div>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-hidden">
        {messages.length === 0 ? (
          <EmptyState />
        ) : (
          <div 
            className="h-full overflow-y-auto px-4 py-6 space-y-1"
            role="log"
            aria-label="Chat messages"
          >
            {messages.map((message: ChatMessage) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            
            {/* Typing Indicator */}
            {isTyping && (
              <div className="flex justify-start mb-4">
                <div className="max-w-[70%] bg-gray-100 rounded-2xl rounded-bl-md px-4 py-3">
                  <TypingIndicator />
                </div>
              </div>
            )}
            
            {/* Auto-scroll anchor */}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t bg-white">
        <ChatInput
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

export default ChatContainer