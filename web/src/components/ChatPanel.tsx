import { useEffect, useRef, useState, type FormEvent } from 'react'
import Markdown from 'react-markdown'
import { HeartPulse, Send } from 'lucide-react'
import { useChat } from '../chat/ChatContext'

function AssistantAvatar() {
  return (
    <span className="avatar avatar-ai" aria-hidden="true">
      <HeartPulse size={18} />
    </span>
  )
}

export function ChatPanel() {
  const { messages, pending, send } = useChat()
  const [draft, setDraft] = useState('')
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages, pending])

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const text = draft.trim()
    if (!text || pending) return
    setDraft('')
    void send(text)
  }

  return (
    <div className="chat">
      <div className="chat-messages" role="log" aria-live="polite" aria-label="Conversation">
        {messages.length === 0 && (
          <div className="msg">
            <AssistantAvatar />
            <div className="bubble bubble-assistant">
              <p>Hello, I'm HealthAgent. Ask me a health question, or tell me a reading such as "my BP is 120/80".</p>
            </div>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`msg msg-${msg.role}`}>
            {msg.role === 'assistant' && <AssistantAvatar />}
            <div className={`bubble bubble-${msg.role}`}>
              <Markdown>{msg.content}</Markdown>
            </div>
          </div>
        ))}
        {pending && (
          <div className="msg">
            <AssistantAvatar />
            <div className="bubble bubble-assistant bubble-pending">
              <span className="dots" aria-hidden="true">
                <i />
                <i />
                <i />
              </span>
              Thinking...
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <form className="chat-input" onSubmit={handleSubmit}>
        <input
          type="text"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Ask me about your health..."
          aria-label="Message"
        />
        <button type="submit" className="btn btn-primary btn-icon" disabled={pending || !draft.trim()} aria-label="Send message">
          <Send className="icon" size={18} aria-hidden="true" />
        </button>
      </form>
      <p className="caption chat-disclaimer">HealthAgent provides general information, not medical advice.</p>
    </div>
  )
}
