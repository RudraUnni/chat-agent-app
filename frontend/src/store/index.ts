import { configureStore } from '@reduxjs/toolkit'
import chatReducer from './slices/chatSlice'
import connectionReducer from './slices/connectionSlice'
import { websocketMiddleware } from './middleware/websocketMiddleware'

export const store = configureStore({
  reducer: {
    chat: chatReducer,
    connection: connectionReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore WebSocket instance in actions
        ignoredActions: ['connection/setWebSocket'],
        ignoredPaths: ['connection.ws'],
      },
    }).concat(websocketMiddleware),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch