const TypingIndicator = () => {
  return (
    <div className="py-2">
      <div className="inline-flex items-center space-x-2 px-3 py-2 bg-white border rounded-lg shadow-sm">
        <div className="flex space-x-1">
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
        </div>
        <span className="text-xs text-gray-500">Assistant is typing…</span>
      </div>
    </div>
  )
}

export default TypingIndicator