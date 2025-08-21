import { Link } from 'react-router-dom'
import { MessageCircle, ArrowRight, Sparkles, Zap, Shield, Hash } from 'lucide-react'
import { useMessages, useIsConnected } from '../../store/hooks'

const Home = () => {
  const messages = useMessages()
  const isConnected = useIsConnected()
  const messageCount = messages.length

  const features = [
    {
      icon: <Sparkles className="w-6 h-6" />,
      title: "Medical Research",
      description: "Access to PubMed database for evidence-based medical information"
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Real-time",
      description: "Instant responses with WebSocket technology"
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Reliable",
      description: "Evidence-based medical information from trusted sources"
    }
  ]

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <div className="inline-flex items-center justify-center w-20 h-20 bg-primary-100 rounded-full mb-6">
          <MessageCircle className="w-10 h-10 text-primary-600" />
        </div>
        
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to Medical Assistant
        </h1>
        
        <p className="text-xl text-gray-600 mb-8">
          Your intelligent medical research assistant powered by PubMed
        </p>

        {/* Connection Status & Message Count */}
        <div className="flex items-center justify-center space-x-6 mb-8">
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-gray-400'}`} />
            <span className="text-sm text-gray-600">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          
          {messageCount > 0 && (
            <div className="flex items-center space-x-2">
              <Hash className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-600">
                {messageCount} message{messageCount !== 1 ? 's' : ''} in session
              </span>
            </div>
          )}
        </div>

        <Link
          to="/chat"
          className="inline-flex items-center px-6 py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 transition-colors duration-200"
        >
          {messageCount > 0 ? 'Continue Conversation' : 'Start Chatting'}
          <ArrowRight className="ml-2 w-5 h-5" />
        </Link>
      </div>

      {/* Features Grid */}
      <div className="grid md:grid-cols-3 gap-6 mb-12">
        {features.map((feature, index) => (
          <div
            key={index}
            className="bg-white p-6 rounded-lg border border-gray-200 hover:shadow-lg transition-shadow duration-200"
          >
            <div className="text-primary-600 mb-4">{feature.icon}</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {feature.title}
            </h3>
            <p className="text-gray-600">{feature.description}</p>
          </div>
        ))}
      </div>

      {/* Info Section */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-blue-900 mb-2">
          ✨ Persistent Conversation
        </h2>
        <p className="text-blue-700">
          Your chat session remains active even when you navigate away from the chat page. 
          Messages continue streaming in the background, and you can pick up right where you left off!
        </p>
      </div>
    </div>
  )
}

export default Home