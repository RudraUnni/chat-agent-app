import { useEffect, useRef, useState } from 'react'
import { AlertCircle, Wifi, WifiOff, Menu } from 'lucide-react'
import MessageBubble from './MessageBubble'
import ConversationSidebar from './ConversationSidebar'
import { 
  useAppDispatch, 
  useMessages, 
  useIsConnected, 
  useIsTyping, 
  useConnectionError,
  useCurrentUser,
  useCurrentConversationId,
  useConversationHistory,
  useConversationHistoryLoading
} from '../../store/hooks'
import { sendChatMessage, connectWebSocket } from '../../store/actions/websocketActions'
import { setConnectionError } from '../../store/slices/connectionSlice'
import { setMessages } from '../../store/slices/chatSlice'
import { fetchConversationHistory, loadConversationFromStorage } from '../../store/slices/conversationSlice'
import { createDummyUser, setCurrentUser, loadUserFromStorage } from '../../store/slices/userSlice'
import type { ChatMessage } from '../../types/chat'
import ChatInput from './ChatInput'
import TypingIndicator from '../../pages/Chat/components/TypingIndicator'

const ChatContainer = () => {
  const dispatch = useAppDispatch()
  const messages = useMessages()
  const isConnected = useIsConnected()
  const isTyping = useIsTyping()
  const connectionError = useConnectionError()
  const currentUser = useCurrentUser()
  const currentConversationId = useCurrentConversationId()
  const conversationHistory = useConversationHistory()
  const isLoadingHistory = useConversationHistoryLoading()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [isInitialized, setIsInitialized] = useState(false)

  const handleSendMessage = (content: string) => {
    console.log('🎯 handleSendMessage called with:', { content, isConnected })
    if (!content.trim() || !isConnected) {
      console.log('❌ Not sending message - empty content or not connected')
      return
    }

    console.log('✅ Dispatching sendChatMessage')
    dispatch(sendChatMessage(content) as any)
  }

  const clearError = () => {
    dispatch(setConnectionError(null))
  }

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  // Auto-setup default user on mount
  useEffect(() => {
    const initializeApp = async () => {
      if (!isInitialized) {
        try {
          // Try to load user from storage first
          dispatch(loadUserFromStorage())
          setIsInitialized(true)
        } catch (error) {
          console.error('Failed to load user from storage:', error)
          setIsInitialized(true)
        }
      }
    }

    initializeApp()
  }, [dispatch, isInitialized])

  // Create user if none exists
  useEffect(() => {
    const createUserIfNeeded = async () => {
      if (isInitialized && !currentUser) {
        try {
          console.log('No user found, creating default test user...')
          await dispatch(createDummyUser()).unwrap()
        } catch (error) {
          console.error('Failed to create dummy user:', error)
        }
      }
    }

    createUserIfNeeded()
  }, [dispatch, isInitialized, currentUser])

  // Separate effect to handle WebSocket connection after user is ready
  useEffect(() => {
    if (isInitialized && currentUser) {
      console.log('User ready, loading conversation and connecting WebSocket...')
      
      // Load conversation from storage
      dispatch(loadConversationFromStorage())
      
      // Connect WebSocket with user context
      setTimeout(() => {
        dispatch(connectWebSocket())
      }, 100)
    }
  }, [dispatch, isInitialized, currentUser])

  // Load conversation history when conversation changes
  useEffect(() => {
    if (currentConversationId && isInitialized && currentUser) {
      // Check if we already have history for this conversation
      const existingHistory = conversationHistory[currentConversationId]
      if (!existingHistory) {
        dispatch(fetchConversationHistory(currentConversationId))
      } else {
        // Load existing history into chat messages
        dispatch(setMessages(existingHistory))
      }
    }
  }, [currentConversationId, isInitialized, currentUser, dispatch, conversationHistory])

  // Update messages when conversation history is loaded
  useEffect(() => {
    if (currentConversationId && conversationHistory[currentConversationId]) {
      const history = conversationHistory[currentConversationId]
      // Only update if messages are different (avoid infinite loops)
      if (JSON.stringify(messages) !== JSON.stringify(history)) {
        dispatch(setMessages(history))
      }
    }
  }, [conversationHistory, currentConversationId, messages, dispatch])

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

  // Show loading while initializing
  if (!isInitialized || !currentUser) {
    return (
      <div className="flex items-center justify-center h-screen bg-white">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Initializing chat...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-white">
      {/* Conversation Sidebar */}
      <ConversationSidebar isOpen={isSidebarOpen} onToggle={() => setIsSidebarOpen(!isSidebarOpen)} />
      
      {/* Main Chat Area */}
      <div className={`flex flex-col flex-1 transition-all duration-300 ${isSidebarOpen ? 'ml-80' : 'ml-0'}`}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b bg-white shadow-sm">
          <div className="flex items-center space-x-3">
            {!isSidebarOpen && (
              <button
                onClick={() => setIsSidebarOpen(true)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Menu className="w-5 h-5 text-gray-600" />
              </button>
            )}
            <h1 className="text-xl font-semibold text-gray-900">Medical Assistant</h1>
            {currentConversationId && (
              <span className="text-sm text-gray-500">
                • Conversation {currentConversationId.slice(-8)}
              </span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            {isLoadingHistory && (
              <div className="flex items-center text-blue-600 mr-3">
                <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mr-2"></div>
                <span className="text-sm font-medium">Loading history...</span>
              </div>
            )}
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
    </div>
  )
}

export default ChatContainer