import MessageList from './components/MessageList'
import MessageInput from './components/MessageInput'
import TypingIndicator from './components/TypingIndicator'
import { AlertCircle, Wifi, WifiOff } from 'lucide-react'
import { useChatStore } from '../../store/chatStore'

const Chat = () => {
  // Get state and actions from the global store
  const messages = useChatStore((state) => state.messages)
  const isConnected = useChatStore((state) => state.isConnected)
  const isTyping = useChatStore((state) => state.isTyping)
  const connectionError = useChatStore((state) => state.connectionError)
  const sendMessage = useChatStore((state) => state.sendMessage)
  const setError = useChatStore((state) => state.setError)

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || !isConnected) return

    try {
      await sendMessage(content)
    } catch (error) {
      console.error('Failed to send message:', error)
      setError('Failed to send message. Please try again.')
    }
  }

  const clearError = () => {
    setError(null)
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
      {connectionError && (
        <div className="mx-4 mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center">
          <AlertCircle className="w-5 h-5 text-red-500 mr-2 flex-shrink-0" />
          <span className="text-red-700">{connectionError}</span>
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