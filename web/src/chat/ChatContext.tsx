import { createContext, useCallback, useContext, useMemo, useRef, useState, type ReactNode } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import { healthLogsQuery } from '../api/queries'
import type { ChatMessage, HealthLog } from '../api/types'
import { useAuth } from '../auth/AuthContext'

interface ChatState {
  messages: ChatMessage[]
  pending: boolean
  send: (text: string) => Promise<void>
}

const ChatContext = createContext<ChatState | null>(null)

function errorText(err: unknown): string {
  return err instanceof Error ? err.message : String(err)
}

/**
 * Holds the conversation above the router so it survives page navigation and a
 * reply still lands if the user leaves the chat page mid-request.
 */
export function ChatProvider({ children }: { children: ReactNode }) {
  const { userId, profile } = useAuth()
  const queryClient = useQueryClient()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [pending, setPending] = useState(false)
  const messagesRef = useRef(messages)
  messagesRef.current = messages

  const send = useCallback(
    async (text: string) => {
      const history = messagesRef.current
      setMessages([...history, { role: 'user', content: text }])
      setPending(true)

      let reply: string
      try {
        if (userId !== null && profile) {
          // The backend's /chat is stateless: it needs the profile and recent logs on every call.
          const logs: HealthLog[] = await queryClient
            .fetchQuery({ ...healthLogsQuery(userId, 90), staleTime: 60_000 })
            .catch(() => [])
          const res = await api.chat({
            message: text,
            user_profile: profile,
            health_logs: logs,
            chat_history: history,
          })
          reply = res.response ?? "Sorry, I couldn't generate a response."
        } else {
          const res = await api.chat({ message: text, chat_history: history })
          reply = res.response ?? "Sorry, I couldn't generate a response."
        }
      } catch (err) {
        reply = `Error communicating with chatbot: ${errorText(err)}`
      }

      // Vitals mentioned in the message ("my BP is 120/80") are logged automatically.
      if (userId !== null) {
        try {
          const metrics = await api.parseMetrics(text)
          if (metrics.length > 0) {
            for (const metric of metrics) {
              await api.createHealthLog(userId, { ...metric, source: 'chatbot' })
            }
            reply += `\n\n📊 **Metrics saved:** ${metrics.map((m) => m.metric_type).join(', ')}`
            void queryClient.invalidateQueries({ queryKey: ['health-logs', userId] })
            void queryClient.invalidateQueries({ queryKey: ['vitals-summary', userId] })
          }
        } catch {
          // Metric logging is best-effort; the chat reply still stands.
        }
      }

      setMessages((current) => [...current, { role: 'assistant', content: reply }])
      setPending(false)
    },
    [userId, profile, queryClient],
  )

  const value = useMemo(() => ({ messages, pending, send }), [messages, pending, send])
  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>
}

export function useChat(): ChatState {
  const ctx = useContext(ChatContext)
  if (!ctx) throw new Error('useChat must be used inside <ChatProvider>')
  return ctx
}
