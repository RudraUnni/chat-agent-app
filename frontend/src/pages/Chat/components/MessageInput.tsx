import { useState } from 'react'
import type { KeyboardEvent } from 'react'
import { Send } from 'lucide-react'
import ErrorBoundary from '../../../components/common/ErrorBoundary'

interface MessageInputProps {
  onSendMessage: (message: string) => void
  disabled?: boolean
  placeholder?: string
}

const MessageInput = ({ onSendMessage, disabled = false, placeholder = "Type your message..." }: MessageInputProps) => {
  const [message, setMessage] = useState('')

  const validateAndSanitizeMessage = (input: string): string => {
    // Basic sanitization - remove excessive whitespace and limit length
    const sanitized = input.trim().replace(/\s+/g, ' ')
    
    // Length validation
    if (sanitized.length > 2000) {
      throw new Error('Message is too long (maximum 2000 characters)')
    }
    
    if (sanitized.length === 0) {
      throw new Error('Message cannot be empty')
    }
    
    return sanitized
  }

  const handleSend = () => {
    if (!disabled) {
      try {
        const sanitizedMessage = validateAndSanitizeMessage(message)
        onSendMessage(sanitizedMessage)
        setMessage('')
      } catch (error) {
        console.error('Message validation failed:', error)
        // Could show user-friendly error here
      }
    }
  }

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <ErrorBoundary>
      <div className="p-4">
        <div className="flex items-end space-x-3">
          <div className="flex-1">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder={placeholder}
              disabled={disabled}
              rows={1}
              maxLength={2000}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
              style={{
                minHeight: '52px',
                maxHeight: '120px'
              }}
              aria-label="Type your message"
            />
          </div>
          <button
            onClick={handleSend}
            disabled={disabled || !message.trim()}
            className="p-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors duration-200"
            title="Send message"
            aria-label="Send message"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <div className="flex justify-between items-center mt-2">
          {!disabled && (
            <p className="text-xs text-gray-500">
              Press Enter to send.
            </p>
          )}
          <p className="text-xs text-gray-400">
            {message.length}/2000
          </p>
        </div>
      </div>
    </ErrorBoundary>
  )
}

export default MessageInput