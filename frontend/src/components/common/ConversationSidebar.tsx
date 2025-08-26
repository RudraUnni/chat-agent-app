import React, { useState, useEffect } from 'react'
import { MessageCircle, Plus, Trash2, Edit2, User, LogOut, Loader2 } from 'lucide-react'
import { 
  useAppDispatch, 
  useCurrentUser, 
  useConversations, 
  useCurrentConversationId,
  useConversationLoading,
  useConversationError
} from '../../store/hooks'
import {
  fetchUserConversations,
  setCurrentConversationId,
  deleteConversation,
  updateConversationTitle,
  clearError,
  addConversation
} from '../../store/slices/conversationSlice'
import { setCurrentUser } from '../../store/slices/userSlice'
import { clearMessages } from '../../store/slices/chatSlice'
import { connectWebSocket, disconnectWebSocket } from '../../store/actions/websocketActions'
import type { Conversation } from '../../store/slices/conversationSlice'

interface ConversationSidebarProps {
  isOpen: boolean
  onToggle: () => void
}

const ConversationSidebar: React.FC<ConversationSidebarProps> = ({ isOpen, onToggle }) => {
  const dispatch = useAppDispatch()
  const currentUser = useCurrentUser()
  const conversations = useConversations()
  const currentConversationId = useCurrentConversationId()
  const isLoading = useConversationLoading()
  const error = useConversationError()
  
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editTitle, setEditTitle] = useState('')

  useEffect(() => {
    if (currentUser) {
      dispatch(fetchUserConversations(currentUser.id))
    }
  }, [dispatch, currentUser])

  const handleNewConversation = () => {
    // Generate new conversation ID
    const newConversationId = `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    
    // Set as current conversation
    dispatch(setCurrentConversationId(newConversationId))
    
    // Clear current messages
    dispatch(clearMessages())
    
    // Reconnect WebSocket with new conversation ID
    dispatch(disconnectWebSocket())
    setTimeout(() => {
      dispatch(connectWebSocket())
    }, 100)
    
    // Add to conversations list (will be persisted when first message is sent)
    if (currentUser) {
      const newConversation: Conversation = {
        id: newConversationId,
        user_id: currentUser.id,
        title: 'New Conversation',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        message_count: 0,
      }
      dispatch(addConversation(newConversation))
    }
  }

  const handleSelectConversation = (conversationId: string) => {
    if (conversationId === currentConversationId) return
    
    dispatch(setCurrentConversationId(conversationId))
    dispatch(clearMessages())
    
    // Reconnect WebSocket with selected conversation
    dispatch(disconnectWebSocket())
    setTimeout(() => {
      dispatch(connectWebSocket())
    }, 100)
  }

  const handleDeleteConversation = async (conversationId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    
    if (window.confirm('Are you sure you want to delete this conversation?')) {
      try {
        await dispatch(deleteConversation(conversationId)).unwrap()
        
        // If we deleted the current conversation, start a new one
        if (conversationId === currentConversationId) {
          handleNewConversation()
        }
      } catch (error) {
        console.error('Failed to delete conversation:', error)
      }
    }
  }

  const handleEditTitle = (conversation: Conversation, e: React.MouseEvent) => {
    e.stopPropagation()
    setEditingId(conversation.id)
    setEditTitle(conversation.title)
  }

  const handleSaveTitle = async (conversationId: string) => {
    if (!editTitle.trim()) return
    
    try {
      await dispatch(updateConversationTitle({ 
        conversationId, 
        title: editTitle.trim() 
      })).unwrap()
      setEditingId(null)
      setEditTitle('')
    } catch (error) {
      console.error('Failed to update title:', error)
    }
  }

  const handleCancelEdit = () => {
    setEditingId(null)
    setEditTitle('')
  }

  const handleLogout = () => {
    // Clear user and disconnect
    dispatch(setCurrentUser(null))
    dispatch(setCurrentConversationId(null))
    dispatch(clearMessages())
    dispatch(disconnectWebSocket())
  }

  const handleClearError = () => {
    dispatch(clearError())
  }

  if (!isOpen) {
    return (
      <button
        onClick={onToggle}
        className="fixed top-4 left-4 z-50 p-2 bg-white border border-gray-200 rounded-lg shadow-lg hover:shadow-xl transition-shadow"
      >
        <MessageCircle className="w-5 h-5 text-gray-600" />
      </button>
    )
  }

  return (
    <div className="fixed inset-y-0 left-0 z-50 w-80 bg-white border-r border-gray-200 shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <User className="w-5 h-5 text-gray-600" />
          <div>
            <div className="font-medium text-gray-900">{currentUser?.username}</div>
            <div className="text-xs text-gray-500">{currentUser?.email}</div>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={handleLogout}
            className="p-1.5 text-gray-500 hover:text-red-600 transition-colors"
            title="Logout"
          >
            <LogOut className="w-4 h-4" />
          </button>
          <button
            onClick={onToggle}
            className="p-1.5 text-gray-500 hover:text-gray-700 transition-colors"
          >
            ×
          </button>
        </div>
      </div>

      {/* New Conversation Button */}
      <div className="p-4 border-b border-gray-200">
        <button
          onClick={handleNewConversation}
          className="w-full flex items-center justify-center space-x-2 py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>New Conversation</span>
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mx-4 mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
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

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="flex items-center justify-center p-8">
            <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
          </div>
        ) : conversations.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <MessageCircle className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p className="text-sm">No conversations yet</p>
            <p className="text-xs mt-1">Start chatting to create your first conversation</p>
          </div>
        ) : (
          <div className="p-2 space-y-1">
            {conversations.map((conversation) => (
              <div
                key={conversation.id}
                onClick={() => handleSelectConversation(conversation.id)}
                className={`
                  group relative p-3 rounded-lg cursor-pointer transition-colors
                  ${conversation.id === currentConversationId 
                    ? 'bg-blue-50 border border-blue-200' 
                    : 'hover:bg-gray-50'
                  }
                `}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    {editingId === conversation.id ? (
                      <div className="space-y-2">
                        <input
                          type="text"
                          value={editTitle}
                          onChange={(e) => setEditTitle(e.target.value)}
                          className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') {
                              handleSaveTitle(conversation.id)
                            } else if (e.key === 'Escape') {
                              handleCancelEdit()
                            }
                          }}
                          autoFocus
                        />
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleSaveTitle(conversation.id)}
                            className="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
                          >
                            Save
                          </button>
                          <button
                            onClick={handleCancelEdit}
                            className="px-2 py-1 text-xs border border-gray-300 rounded hover:bg-gray-50"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <>
                        <h3 className="font-medium text-gray-900 truncate">
                          {conversation.title}
                        </h3>
                        {conversation.last_message_preview && (
                          <p className="text-xs text-gray-500 truncate mt-1">
                            {conversation.last_message_preview}
                          </p>
                        )}
                        <div className="flex items-center justify-between mt-2">
                          <span className="text-xs text-gray-400">
                            {conversation.message_count} messages
                          </span>
                          <span className="text-xs text-gray-400">
                            {new Date(conversation.updated_at).toLocaleDateString()}
                          </span>
                        </div>
                      </>
                    )}
                  </div>
                  
                  {editingId !== conversation.id && (
                    <div className="flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => handleEditTitle(conversation, e)}
                        className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                        title="Edit title"
                      >
                        <Edit2 className="w-3 h-3" />
                      </button>
                      <button
                        onClick={(e) => handleDeleteConversation(conversation.id, e)}
                        className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                        title="Delete conversation"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default ConversationSidebar