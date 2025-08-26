import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit'
import { API_ENDPOINTS } from '../../utils/constants'
import type { ChatMessage } from '../../types/chat'

export interface Conversation {
  id: string
  user_id: string
  title: string
  created_at: string
  updated_at: string
  message_count: number
  last_message_preview?: string
}

export interface ConversationWithMessages extends Conversation {
  messages: ChatMessage[]
}

interface ConversationState {
  conversations: Conversation[]
  currentConversationId: string | null
  conversationHistory: { [conversationId: string]: ChatMessage[] }
  isLoading: boolean
  isLoadingHistory: boolean
  error: string | null
}

const initialState: ConversationState = {
  conversations: [],
  currentConversationId: null,
  conversationHistory: {},
  isLoading: false,
  isLoadingHistory: false,
  error: null,
}

// Async thunks for conversation operations
export const fetchUserConversations = createAsyncThunk(
  'conversation/fetchUserConversations',
  async (userId: string, { rejectWithValue }) => {
    try {
      const response = await fetch(`${API_ENDPOINTS.BASE_URL}/conversations/?user_id=${userId}`)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const conversations = await response.json()
      return conversations
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to fetch conversations')
    }
  }
)

export const fetchConversationHistory = createAsyncThunk(
  'conversation/fetchHistory',
  async (conversationId: string, { rejectWithValue }) => {
    try {
      const response = await fetch(`${API_ENDPOINTS.BASE_URL}/conversations/${conversationId}/messages`)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const messages = await response.json()
      
      // Convert to ChatMessage format
      const chatMessages: ChatMessage[] = messages.map((msg: any) => ({
        id: msg.id,
        content: msg.content,
        role: msg.role,
        timestamp: new Date(msg.created_at).getTime(),
        status: 'delivered' as const
      }))

      return { conversationId, messages: chatMessages }
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to fetch conversation history')
    }
  }
)

export const deleteConversation = createAsyncThunk(
  'conversation/delete',
  async (conversationId: string, { rejectWithValue }) => {
    try {
      const response = await fetch(`${API_ENDPOINTS.BASE_URL}/conversations/${conversationId}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return conversationId
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to delete conversation')
    }
  }
)

export const updateConversationTitle = createAsyncThunk(
  'conversation/updateTitle',
  async ({ conversationId, title }: { conversationId: string; title: string }, { rejectWithValue }) => {
    try {
      const response = await fetch(
        `${API_ENDPOINTS.BASE_URL}/conversations/${conversationId}/title?title=${encodeURIComponent(title)}`,
        {
          method: 'PATCH',
        }
      )

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return { conversationId, title }
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to update conversation title')
    }
  }
)

const conversationSlice = createSlice({
  name: 'conversation',
  initialState,
  reducers: {
    setCurrentConversationId: (state, action: PayloadAction<string | null>) => {
      state.currentConversationId = action.payload
      // Store in localStorage for persistence
      if (action.payload) {
        localStorage.setItem('currentConversationId', action.payload)
      } else {
        localStorage.removeItem('currentConversationId')
      }
    },
    
    loadConversationFromStorage: (state) => {
      const stored = localStorage.getItem('currentConversationId')
      if (stored) {
        state.currentConversationId = stored
      }
    },
    
    addConversation: (state, action: PayloadAction<Conversation>) => {
      const exists = state.conversations.find(conv => conv.id === action.payload.id)
      if (!exists) {
        state.conversations.unshift(action.payload)
      }
    },
    
    updateConversationInList: (state, action: PayloadAction<Partial<Conversation> & { id: string }>) => {
      const index = state.conversations.findIndex(conv => conv.id === action.payload.id)
      if (index !== -1) {
        state.conversations[index] = { ...state.conversations[index], ...action.payload }
      }
    },
    
    clearHistory: (state, action: PayloadAction<string>) => {
      delete state.conversationHistory[action.payload]
    },
    
    clearAllHistory: (state) => {
      state.conversationHistory = {}
    },
    
    clearError: (state) => {
      state.error = null
    },
  },
  
  extraReducers: (builder) => {
    // Fetch user conversations
    builder
      .addCase(fetchUserConversations.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(fetchUserConversations.fulfilled, (state, action) => {
        state.isLoading = false
        state.conversations = action.payload
      })
      .addCase(fetchUserConversations.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
      })

    // Fetch conversation history
    builder
      .addCase(fetchConversationHistory.pending, (state) => {
        state.isLoadingHistory = true
        state.error = null
      })
      .addCase(fetchConversationHistory.fulfilled, (state, action) => {
        state.isLoadingHistory = false
        state.conversationHistory[action.payload.conversationId] = action.payload.messages
      })
      .addCase(fetchConversationHistory.rejected, (state, action) => {
        state.isLoadingHistory = false
        state.error = action.payload as string
      })

    // Delete conversation
    builder
      .addCase(deleteConversation.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(deleteConversation.fulfilled, (state, action) => {
        state.isLoading = false
        state.conversations = state.conversations.filter(conv => conv.id !== action.payload)
        delete state.conversationHistory[action.payload]
        if (state.currentConversationId === action.payload) {
          state.currentConversationId = null
          localStorage.removeItem('currentConversationId')
        }
      })
      .addCase(deleteConversation.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
      })

    // Update conversation title
    builder
      .addCase(updateConversationTitle.pending, (state) => {
        state.error = null
      })
      .addCase(updateConversationTitle.fulfilled, (state, action) => {
        const conversation = state.conversations.find(conv => conv.id === action.payload.conversationId)
        if (conversation) {
          conversation.title = action.payload.title
        }
      })
      .addCase(updateConversationTitle.rejected, (state, action) => {
        state.error = action.payload as string
      })
  },
})

export const {
  setCurrentConversationId,
  loadConversationFromStorage,
  addConversation,
  updateConversationInList,
  clearHistory,
  clearAllHistory,
  clearError,
} = conversationSlice.actions

export default conversationSlice.reducer