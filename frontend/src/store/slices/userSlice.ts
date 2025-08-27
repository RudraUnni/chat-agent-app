import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit'
import { API_ENDPOINTS } from '../../utils/constants'

export interface User {
  id: string
  username: string
  email: string
  created_at: string
}

interface UserState {
  currentUser: User | null
  isLoading: boolean
  error: string | null
}

const initialState: UserState = {
  currentUser: null,
  isLoading: false,
  error: null,
}

// Async thunks for user operations
export const createDummyUser = createAsyncThunk(
  'user/createDummy',
  async (_, { rejectWithValue }) => {
    try {
      const response = await fetch(`${API_ENDPOINTS.BASE_URL}/users/dummy`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const user = await response.json()
      return user
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to create user')
    }
  }
)



const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setCurrentUser: (state, action: PayloadAction<User | null>) => {
      state.currentUser = action.payload
      // Store in localStorage for persistence
      if (action.payload) {
        localStorage.setItem('currentUser', JSON.stringify(action.payload))
      } else {
        localStorage.removeItem('currentUser')
      }
    },
    
    loadUserFromStorage: (state) => {
      const stored = localStorage.getItem('currentUser')
      if (stored) {
        try {
          state.currentUser = JSON.parse(stored)
        } catch (error) {
          console.error('Failed to parse stored user:', error)
          localStorage.removeItem('currentUser')
        }
      }
    },
    
    clearError: (state) => {
      state.error = null
    },
  },
  
  extraReducers: (builder) => {
    // Create dummy user
    builder
      .addCase(createDummyUser.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(createDummyUser.fulfilled, (state, action) => {
        state.isLoading = false
        state.currentUser = action.payload
        // Store in localStorage
        localStorage.setItem('currentUser', JSON.stringify(action.payload))
      })
      .addCase(createDummyUser.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
      })


  },
})

export const { setCurrentUser, loadUserFromStorage, clearError } = userSlice.actions
export default userSlice.reducer