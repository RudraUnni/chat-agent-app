import { formatDistanceToNow } from 'date-fns'
import { Check, AlertCircle, Clock } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { ChatMessage } from '../../types/chat'
import clsx from 'clsx'

interface MessageBubbleProps {
  message: ChatMessage
}

const MessageBubble = ({ message }: MessageBubbleProps) => {
  const isUser = message.role === 'user'
  
  const getStatusIcon = () => {
    switch (message.status) {
      case 'sending':
        return (
          <div className="flex items-center">
            <div className="animate-pulse w-2 h-2 bg-gray-400 rounded-full mr-1"></div>
            <Clock className="w-3 h-3 text-gray-400" />
          </div>
        )
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
      'flex w-full mb-4',
      isUser ? 'justify-end' : 'justify-start'
    )}>
      <div className={clsx(
        'max-w-[70%] rounded-2xl px-4 py-3 shadow-sm',
        isUser 
          ? 'bg-blue-600 text-white rounded-br-md' 
          : 'bg-gray-100 text-gray-900 rounded-bl-md'
      )}>
        {/* Message content */}
        <div className="break-words">
          {isUser ? (
            // User messages: plain text with whitespace preserved
            <div className="whitespace-pre-wrap">
              {message.content}
            </div>
          ) : (
            // Assistant messages: render markdown
            <div className="prose prose-sm max-w-none prose-gray">
              <ReactMarkdown 
                remarkPlugins={[remarkGfm]}
                components={{
                  // Custom styling for markdown elements
                  h1: ({children}) => <h1 className="text-lg font-bold text-gray-900 mb-2">{children}</h1>,
                  h2: ({children}) => <h2 className="text-base font-semibold text-gray-900 mb-2">{children}</h2>,
                  h3: ({children}) => <h3 className="text-sm font-medium text-gray-900 mb-1">{children}</h3>,
                  p: ({children}) => <p className="text-gray-900 mb-2 last:mb-0">{children}</p>,
                  ul: ({children}) => <ul className="list-disc list-inside mb-2 text-gray-900">{children}</ul>,
                  ol: ({children}) => <ol className="list-decimal list-inside mb-2 text-gray-900">{children}</ol>,
                  li: ({children}) => <li className="mb-1">{children}</li>,
                  blockquote: ({children}) => (
                    <blockquote className="border-l-4 border-gray-300 pl-4 italic text-gray-700 mb-2">
                      {children}
                    </blockquote>
                  ),
                  code: ({inline, children}) => (
                    inline ? (
                      <code className="bg-gray-200 px-1 py-0.5 rounded text-sm font-mono text-gray-800">
                        {children}
                      </code>
                    ) : (
                      <code className="block bg-gray-800 text-gray-100 p-3 rounded-lg text-sm font-mono overflow-x-auto mb-2">
                        {children}
                      </code>
                    )
                  ),
                  pre: ({children}) => (
                    <pre className="bg-gray-800 text-gray-100 p-3 rounded-lg text-sm font-mono overflow-x-auto mb-2">
                      {children}
                    </pre>
                  ),
                  table: ({children}) => (
                    <div className="overflow-x-auto mb-2">
                      <table className="min-w-full border-collapse border border-gray-300 text-sm">
                        {children}
                      </table>
                    </div>
                  ),
                  thead: ({children}) => (
                    <thead className="bg-gray-50">
                      {children}
                    </thead>
                  ),
                  th: ({children}) => (
                    <th className="border border-gray-300 px-3 py-2 text-left font-medium text-gray-900">
                      {children}
                    </th>
                  ),
                  td: ({children}) => (
                    <td className="border border-gray-300 px-3 py-2 text-gray-900">
                      {children}
                    </td>
                  ),
                  strong: ({children}) => <strong className="font-semibold text-gray-900">{children}</strong>,
                  em: ({children}) => <em className="italic text-gray-900">{children}</em>,
                  a: ({href, children}) => (
                    <a 
                      href={href} 
                      className="text-blue-600 hover:text-blue-800 underline"
                      target="_blank" 
                      rel="noopener noreferrer"
                    >
                      {children}
                    </a>
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
              {/* Show streaming cursor for assistant messages that are being sent */}
              {message.status === 'sending' && (
                <span className="animate-pulse text-gray-600 ml-1">▋</span>
              )}
            </div>
          )}
        </div>
        
        {/* Message metadata */}
        <div className={clsx(
          'flex items-center justify-between mt-2 text-xs',
          isUser ? 'text-blue-100' : 'text-gray-500'
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

export default MessageBubble