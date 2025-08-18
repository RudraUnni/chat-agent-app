export const API_ENDPOINTS = {
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  WS_URL: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/chat',
} as const

export const MESSAGE_STATUS = {
  SENDING: 'sending',
  SENT: 'sent',
  DELIVERED: 'delivered',
  ERROR: 'error',
} as const

export type MessageStatus = typeof MESSAGE_STATUS[keyof typeof MESSAGE_STATUS]

export const MESSAGE_TYPES = {
  MESSAGE: 'message',
  TYPING: 'typing',
  ERROR: 'error',
  CONNECTED: 'connected',
  DISCONNECTED: 'disconnected',
} as const

export const ROUTES = {
  HOME: '/',
  CHAT: '/chat',
} as const