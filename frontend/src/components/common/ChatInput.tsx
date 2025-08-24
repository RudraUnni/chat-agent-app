import { useState, useRef, useEffect } from 'react'
import type { KeyboardEvent } from 'react'
import { Send } from 'lucide-react'

interface ChatInputProps {
  onSendMessage: (message: string) => void
  disabled?: boolean
  placeholder?: string
}

const ChatInput = ({ 
  onSendMessage, 
  disabled = false, 
  placeholder = "Type your message..." 
}: ChatInputProps) => {
  const [message, setMessage] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const validateAndSanitizeMessage = (input: string): string => {
    // Basic sanitization - remove excessive whitespace and limit length
    const sanitized = input.trim().replace(/\s+/g, ' ')
    
    // Length validation
    if (sanitized.length > 4000) {
      throw new Error('Message is too long (maximum 4000 characters)')
    }
    
    if (sanitized.length === 0) {
      throw new Error('Message cannot be empty')
    }
    
    return sanitized
  }

  const handleSend = () => {
    if (!disabled && message.trim()) {
      try {
        const sanitizedMessage = validateAndSanitizeMessage(message)
        onSendMessage(sanitizedMessage)
        setMessage('')
        // Reset textarea height
        if (textareaRef.current) {
          textareaRef.current.style.height = 'auto'
        }
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

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [message])

  return (
    <div className="p-4">
      <div className="flex items-end space-x-3 max-w-4xl mx-auto">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            maxLength={4000}
            className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed transition-colors duration-200"
            style={{
              minHeight: '52px',
              maxHeight: '120px'
            }}
            aria-label="Type your message"
          />
          
          {/* Send button positioned inside textarea */}
          <button
            onClick={handleSend}
            disabled={disabled || !message.trim()}
            className="absolute right-2 bottom-2 p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors duration-200"
            title="Send message"
            aria-label="Send message"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
      
      {/* Helper text */}
      <div className="flex justify-between items-center mt-2 max-w-4xl mx-auto px-1">
        {!disabled && (
          <p className="text-xs text-gray-500">
            Press Enter to send.
          </p>
        )}
        <p className="text-xs text-gray-400">
          {message.length}/4000
        </p>
      </div>
    </div>
  )
}

export default ChatInput