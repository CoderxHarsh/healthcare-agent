import { useEffect, useRef, useState, type FormEvent } from 'react'
import Markdown from 'react-markdown'
import { useChat } from '../chat/ChatContext'

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
      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`bubble bubble-${msg.role}`}>
            <Markdown>{msg.content}</Markdown>
          </div>
        ))}
        {pending && <div className="bubble bubble-assistant bubble-pending">Thinking...</div>}
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
        <button type="submit" className="btn btn-primary" disabled={pending || !draft.trim()}>
          Send
        </button>
      </form>
    </div>
  )
}
