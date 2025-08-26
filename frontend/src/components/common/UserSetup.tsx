import React, { useState, useEffect } from 'react'
import { User, UserPlus, Loader2 } from 'lucide-react'
import { 
  useAppDispatch, 
  useCurrentUser, 
  useUsers, 
  useUserLoading, 
  useUserError 
} from '../../store/hooks'
import { 
  createDummyUser, 
  createUser, 
  fetchUsers, 
  setCurrentUser, 
  loadUserFromStorage,
  clearError 
} from '../../store/slices/userSlice'

interface UserSetupProps {
  onUserSelected: () => void
}

const UserSetup: React.FC<UserSetupProps> = ({ onUserSelected }) => {
  const dispatch = useAppDispatch()
  const currentUser = useCurrentUser()
  const users = useUsers()
  const isLoading = useUserLoading()
  const error = useUserError()
  
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')

  useEffect(() => {
    // Load user from localStorage on mount
    dispatch(loadUserFromStorage())
    
    // If we have a user from storage, proceed to chat
    if (currentUser) {
      onUserSelected()
    } else {
      // Fetch existing users
      dispatch(fetchUsers())
    }
  }, [dispatch, currentUser, onUserSelected])

  const handleCreateDummyUser = async () => {
    try {
      await dispatch(createDummyUser()).unwrap()
      onUserSelected()
    } catch (error) {
      console.error('Failed to create dummy user:', error)
    }
  }

  const handleCreateCustomUser = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!username.trim() || !email.trim()) return

    try {
      await dispatch(createUser({ username: username.trim(), email: email.trim() })).unwrap()
      setShowCreateForm(false)
      setUsername('')
      setEmail('')
      onUserSelected()
    } catch (error) {
      console.error('Failed to create custom user:', error)
    }
  }

  const handleSelectUser = (user: typeof currentUser) => {
    dispatch(setCurrentUser(user))
    onUserSelected()
  }

  const handleClearError = () => {
    dispatch(clearError())
  }

  if (currentUser) {
    return null // User is already selected, let the parent handle next steps
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-lg max-w-md w-full p-6">
        <div className="text-center mb-6">
          <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
            <User className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Welcome to Medical Assistant</h1>
          <p className="text-gray-600">Select or create a user to start chatting with history persistence</p>
        </div>

        {error && (
          <div className="mb-6 p-3 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-red-700 text-sm">{error}</span>
              <button
                onClick={handleClearError}
                className="text-red-500 hover:text-red-700 font-bold text-lg leading-none"
              >
                ×
              </button>
            </div>
          </div>
        )}

        {/* Quick Start with Dummy User */}
        <div className="mb-6">
          <button
            onClick={handleCreateDummyUser}
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 px-4 rounded-lg font-medium hover:from-blue-600 hover:to-purple-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Creating User...
              </>
            ) : (
              <>
                <UserPlus className="w-4 h-4 mr-2" />
                Quick Start (Create Test User)
              </>
            )}
          </button>
        </div>

        <div className="text-center mb-4">
          <span className="text-gray-500 text-sm">or</span>
        </div>

        {/* Existing Users */}
        {users.length > 0 && (
          <div className="mb-6">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Select Existing User:</h3>
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {users.map((user) => (
                <button
                  key={user.id}
                  onClick={() => handleSelectUser(user)}
                  className="w-full text-left p-3 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
                >
                  <div className="font-medium text-gray-900">{user.username}</div>
                  <div className="text-sm text-gray-500">{user.email}</div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Create Custom User */}
        <div>
          {!showCreateForm ? (
            <button
              onClick={() => setShowCreateForm(true)}
              className="w-full text-blue-600 hover:text-blue-700 py-2 text-sm font-medium transition-colors"
            >
              Create Custom User
            </button>
          ) : (
            <form onSubmit={handleCreateCustomUser} className="space-y-4">
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
                  Username
                </label>
                <input
                  type="text"
                  id="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter username"
                  required
                />
              </div>
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter email"
                  required
                />
              </div>
              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateForm(false)
                    setUsername('')
                    setEmail('')
                  }}
                  className="flex-1 py-2 px-4 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isLoading || !username.trim() || !email.trim()}
                  className="flex-1 py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? 'Creating...' : 'Create User'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}

export default UserSetup