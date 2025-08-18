import { Link, useLocation } from 'react-router-dom'
import { MessageCircle, Home, Wifi, WifiOff } from 'lucide-react'
import clsx from 'clsx'
import { useIsConnected } from '../../store/hooks'

const Header = () => {
  const location = useLocation()
  const isConnected = useIsConnected()

  const navItems = [
    { path: '/', label: 'Home', icon: Home },
    { path: '/chat', label: 'Chat', icon: MessageCircle },
  ]

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <MessageCircle className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-semibold text-gray-900">
              Chat Agent
            </span>
          </Link>

          {/* Connection Status & Navigation */}
          <div className="flex items-center space-x-4">
            {/* Connection Status */}
            <div className="flex items-center">
              {isConnected ? (
                <div className="flex items-center text-green-600">
                  <Wifi className="w-4 h-4 mr-1" />
                  <span className="text-xs font-medium">Online</span>
                </div>
              ) : (
                <div className="flex items-center text-gray-400">
                  <WifiOff className="w-4 h-4 mr-1" />
                  <span className="text-xs font-medium">Offline</span>
                </div>
              )}
            </div>
            
            {/* Navigation */}
            <nav className="flex space-x-1" role="navigation" aria-label="Main navigation">
              {navItems.map(({ path, label, icon: Icon }) => (
              <Link
                key={path}
                to={path}
                className={clsx(
                  'flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200',
                  location.pathname === path
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                )}
                aria-current={location.pathname === path ? 'page' : undefined}
              >
                <Icon className="w-4 h-4" aria-hidden="true" />
                <span>{label}</span>
              </Link>
            ))}
            </nav>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header