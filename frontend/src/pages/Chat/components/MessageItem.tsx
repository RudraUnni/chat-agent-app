import { formatDistanceToNow } from 'date-fns'
import { Check, AlertCircle, Clock } from 'lucide-react'
import type { ChatMessage } from '../../../types/chat'
import clsx from 'clsx'

interface MessageItemProps {
  message: ChatMessage
}

const MessageItem = ({ message }: MessageItemProps) => {
  const isUser = message.role === 'user'
  
  const getStatusIcon = () => {
    switch (message.status) {
      case 'sending':
        return <Clock className="w-3 h-3 text-gray-400" />
      case 'sent':
        return <Check className="w-3 h-3 text-gray-400" />
      case 'error':
        return <AlertCircle className="w-3 h-3 text-red-500" />
      default:
        return null
    }
  }

  const formatTime = (timestampMs: number) => {
    try {
      return formatDistanceToNow(new Date(timestampMs), { addSuffix: true })
    } catch {
      return 'Just now'
    }
  }

  return (
    <div className={clsx(
      'flex w-full',
      isUser ? 'justify-end' : 'justify-start'
    )}>
      <div className={clsx(
        'max-w-xs lg:max-w-md xl:max-w-lg px-4 py-3 rounded-lg shadow-sm',
        isUser 
          ? 'bg-primary-600 text-white message-user' 
          : 'bg-white border text-gray-900 message-assistant'
      )}>
        {/* Message content */}
        <div className="whitespace-pre-wrap break-words">
          {message.content}
        </div>
        
        {/* Message metadata */}
        <div className={clsx(
          'flex items-center justify-between mt-2 text-xs',
          isUser ? 'text-primary-100' : 'text-gray-500'
        )}>
          <span>{formatTime(message.timestamp)}</span>
          {isUser && (
            <div className="ml-2">
              {getStatusIcon()}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default MessageItem