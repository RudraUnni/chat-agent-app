# State Management Architecture

## Overview
The application uses **Redux Toolkit** for global state management with a custom WebSocket middleware for real-time communication. The WebSocket connection persists across route navigation, ensuring messages continue streaming even when users leave the chat page.

## Core Architecture

### 1. Store Structure
```
src/store/
├── index.ts                    # Store configuration
├── slices/
│   ├── chatSlice.ts           # Messages, typing indicator
│   └── connectionSlice.ts     # WebSocket state
├── middleware/
│   └── websocketMiddleware.ts # WebSocket side effects
├── actions/
│   └── websocketActions.ts    # Action creators
└── hooks.ts                    # Typed Redux hooks
```

### 2. Data Flow
```
User Action → Dispatch → Middleware → WebSocket
                ↓           ↓
            Reducer ← Server Response
                ↓
            UI Update
```

## Key Components

### Store Configuration (`store/index.ts`)
```typescript
export const store = configureStore({
  reducer: {
    chat: chatReducer,
    connection: connectionReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['connection/setWebSocket'],
        ignoredPaths: ['connection.ws'],
      },
    }).concat(websocketMiddleware),
})
```

### Chat Slice (`store/slices/chatSlice.ts`)
Manages chat messages and UI state:
```typescript
interface ChatState {
  messages: ChatMessage[]      // All chat messages
  isTyping: boolean            // Assistant typing indicator
  streamingMessageId: string | null
  error: string | null
}

// Key actions:
- addMessage()               // Add new message
- updateMessage()           // Update existing (for streaming)
- handleIncomingMessage()   // Process WebSocket messages
```

### Connection Slice (`store/slices/connectionSlice.ts`)
Manages WebSocket lifecycle:
```typescript
interface ConnectionState {
  ws: WebSocket | null         // WebSocket instance
  isConnected: boolean        
  isConnecting: boolean       
  reconnectAttempts: number   // For exponential backoff
}

// Key actions:
- setConnected()            // Update connection status
- incrementReconnectAttempts()
- disconnect()              // Clean disconnection
```

### WebSocket Middleware (`store/middleware/websocketMiddleware.ts`)
Handles all WebSocket side effects:
```typescript
export const websocketMiddleware: Middleware = (store) => {
  return (next) => (action) => {
    switch (action.type) {
      case 'websocket/connect':
        // Create WebSocket connection
        // Setup event handlers
        // Auto-reconnect logic
        break
      
      case 'websocket/send':
        // Send message through WebSocket
        ws.send(JSON.stringify(action.payload))
        break
    }
    return next(action)
  }
}
```

**Features:**
- Automatic reconnection with exponential backoff
- Handles connection lifecycle (open, close, error)
- Processes incoming messages and dispatches to reducers

### Action Creators (`store/actions/websocketActions.ts`)
```typescript
// WebSocket operations
export const connectWebSocket = () => ({
  type: 'websocket/connect'
})

// Send chat message (thunk)
export const sendChatMessage = (content: string) => (dispatch) => {
  // 1. Add user message to store
  dispatch(addMessage(userMessage))
  
  // 2. Send via WebSocket
  dispatch(sendWebSocketMessage(wsMessage))
  
  // 3. Update UI state
  dispatch(setTyping(true))
}
```

### Typed Hooks (`store/hooks.ts`)
Type-safe hooks for components:
```typescript
export const useAppDispatch = () => useDispatch<AppDispatch>()
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector

// Convenience selectors
export const useMessages = () => useAppSelector(state => state.chat.messages)
export const useIsConnected = () => useAppSelector(state => state.connection.isConnected)
```

## Component Integration

### Provider Setup (`main.tsx`)
```typescript
<Provider store={store}>
  <WebSocketProvider>  {/* Initiates connection */}
    <App />
  </WebSocketProvider>
</Provider>
```

### Using in Components (`pages/Chat/index.tsx`)
```typescript
const Chat = () => {
  const dispatch = useAppDispatch()
  const messages = useMessages()
  const isConnected = useIsConnected()
  
  const handleSendMessage = (content: string) => {
    dispatch(sendChatMessage(content))
  }
}
```

## WebSocket Lifecycle

### Connection Flow
1. **App Mount** → `WebSocketProvider` dispatches `connectWebSocket()`
2. **Middleware** creates WebSocket instance, sets up handlers
3. **On Open** → Updates store: `isConnected: true`
4. **On Message** → Dispatches `handleIncomingMessage()` to chat slice
5. **On Close** → Auto-reconnect with exponential backoff (1s, 2s, 4s...)

### Message Flow
```typescript
// 1. User sends message
dispatch(sendChatMessage("Hello"))

// 2. Action creator adds to store
{ id: "123", content: "Hello", role: "user", status: "sending" }

// 3. Middleware sends via WebSocket
ws.send({ type: "message", content: "Hello" })

// 4. Server responds
ws.onmessage → handleIncomingMessage()

// 5. Store updates with assistant message
{ id: "124", content: "Hi there!", role: "assistant" }
```

## Persistence Features

### Cross-Navigation Persistence
- WebSocket connection maintained at app level
- Messages stored in Redux (survives route changes)
- Connection status visible on all pages via Header

### Reconnection Strategy
```typescript
// Exponential backoff
Attempt 1: Reconnect after 1 second
Attempt 2: Reconnect after 2 seconds  
Attempt 3: Reconnect after 4 seconds
...
Max attempts: 5
```

### Network Awareness
- Monitors `online/offline` events
- Monitors tab visibility (reconnects when tab becomes active)
- Shows connection status in UI

## State Shape
```typescript
{
  chat: {
    messages: [
      { id: "1", content: "Hello", role: "user", timestamp: 1690000000000 },
      { id: "2", content: "Hi!", role: "assistant", timestamp: 1690000005000 }
    ],
    isTyping: false,
    error: null
  },
  connection: {
    ws: WebSocket,
    isConnected: true,
    isConnecting: false,
    reconnectAttempts: 0
  }
}
```

## Developer Tools

### Redux DevTools
- Install browser extension
- Inspect every action and state change
- Time-travel debugging
- Export/import state

### Debugging WebSocket
```javascript
// In browser console
__REDUX_DEVTOOLS_EXTENSION__.getState()  // View current state
// Filter actions by: websocket/, chat/, connection/
```

## Key Benefits

1. **Single Source of Truth** - All state in Redux store
2. **Predictable Updates** - All changes through actions
3. **Persistent Connection** - WebSocket survives navigation
4. **Type Safety** - Full TypeScript coverage
5. **Scalable** - Clear patterns for adding features
6. **Testable** - Pure reducers, mockable actions