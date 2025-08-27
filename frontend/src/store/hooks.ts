import { useDispatch, useSelector, TypedUseSelectorHook } from 'react-redux'
import type { RootState, AppDispatch } from './index'

// Use throughout your app instead of plain `useDispatch` and `useSelector`
export const useAppDispatch = () => useDispatch<AppDispatch>()
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector

// Chat selectors
export const useMessages = () => useAppSelector(state => state.chat.messages)
export const useIsTyping = () => useAppSelector(state => state.chat.isTyping)
export const useChatError = () => useAppSelector(state => state.chat.error)

// Connection selectors
export const useIsConnected = () => useAppSelector(state => state.connection.isConnected)
export const useIsConnecting = () => useAppSelector(state => state.connection.isConnecting)
export const useConnectionError = () => useAppSelector(state => state.connection.connectionError)

// User selectors
export const useCurrentUser = () => useAppSelector(state => state.user.currentUser)
export const useUserLoading = () => useAppSelector(state => state.user.isLoading)
export const useUserError = () => useAppSelector(state => state.user.error)

// Conversation selectors
export const useConversations = () => useAppSelector(state => state.conversation.conversations)
export const useCurrentConversationId = () => useAppSelector(state => state.conversation.currentConversationId)
export const useConversationHistory = () => useAppSelector(state => state.conversation.conversationHistory)
export const useConversationLoading = () => useAppSelector(state => state.conversation.isLoading)
export const useConversationHistoryLoading = () => useAppSelector(state => state.conversation.isLoadingHistory)
export const useConversationError = () => useAppSelector(state => state.conversation.error)