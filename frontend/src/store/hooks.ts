import { useDispatch, useSelector, TypedUseSelectorHook } from 'react-redux'
import type { RootState, AppDispatch } from './index'

// Use throughout your app instead of plain `useDispatch` and `useSelector`
export const useAppDispatch = () => useDispatch<AppDispatch>()
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector

// Convenience selectors for common state slices
export const useMessages = () => useAppSelector(state => state.chat.messages)
export const useIsTyping = () => useAppSelector(state => state.chat.isTyping)
export const useChatError = () => useAppSelector(state => state.chat.error)
export const useIsConnected = () => useAppSelector(state => state.connection.isConnected)
export const useIsConnecting = () => useAppSelector(state => state.connection.isConnecting)
export const useConnectionError = () => useAppSelector(state => state.connection.connectionError)