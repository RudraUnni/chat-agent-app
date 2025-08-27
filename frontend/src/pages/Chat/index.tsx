import { ThreadPrimitive, AssistantRuntimeProvider, ComposerPrimitive, MessagePrimitive } from '@assistant-ui/react'
import { useFastAPIChatRuntime } from '../../lib/chatRuntime'

const Chat = () => {
  const runtime = useFastAPIChatRuntime()

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <div className="flex flex-col h-full">
        {/* ChatGPT-style header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
            Medical Assistant Chat
          </h1>
        </div>

        {/* Chat thread container */}
        <div className="flex-1 overflow-hidden">
          <ThreadPrimitive.Root className="h-full">
            <div className="h-full flex flex-col bg-white dark:bg-gray-900">
              
              {/* Messages viewport */}
              <ThreadPrimitive.Viewport className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
                <ThreadPrimitive.Messages
                  components={{
                    UserMessage: ({ message }) => (
                      <div className="flex justify-end">
                        <div className="max-w-xs lg:max-w-2xl px-4 py-2 bg-blue-600 text-white rounded-lg">
                          <MessagePrimitive.Root message={message}>
                            <MessagePrimitive.Content />
                          </MessagePrimitive.Root>
                        </div>
                      </div>
                    ),
                    AssistantMessage: ({ message }) => (
                      <div className="flex justify-start">
                        <div className="max-w-xs lg:max-w-2xl px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg">
                          <MessagePrimitive.Root message={message}>
                            <MessagePrimitive.Content />
                          </MessagePrimitive.Root>
                        </div>
                      </div>
                    ),
                  }}
                />
              </ThreadPrimitive.Viewport>

              {/* Scroll to bottom button */}
              <ThreadPrimitive.ScrollToBottom className="fixed bottom-20 right-8">
                <button className="bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 rounded-full p-2 shadow-lg transition-colors">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </ThreadPrimitive.ScrollToBottom>

              {/* Composer */}
              <div className="sticky bottom-0 bg-white dark:bg-gray-900 p-4 border-t border-gray-200 dark:border-gray-700">
                <div className="max-w-4xl mx-auto">
                  <ComposerPrimitive.Root className="flex items-end space-x-2">
                    <ComposerPrimitive.Input
                      autoFocus
                      className="flex-1 p-3 border border-gray-300 dark:border-gray-600 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
                      placeholder="Type your message here... (Press Enter to send, Shift+Enter for new line)"
                      style={{ minHeight: '44px', maxHeight: '200px' }}
                    />
                    <ComposerPrimitive.Send className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg transition-colors">
                      Send
                    </ComposerPrimitive.Send>
                  </ComposerPrimitive.Root>
                </div>
              </div>
            </div>
          </ThreadPrimitive.Root>
        </div>
      </div>
    </AssistantRuntimeProvider>
  )
}

export default Chat