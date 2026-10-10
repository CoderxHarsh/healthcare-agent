import { api } from '../api/client'
import { ChatPanel } from '../components/ChatPanel'
import { Shell } from '../components/Layout'

const FEATURES = [
  { label: '🤖 AI Chat', tone: 'blue' },
  { label: '📊 Vitals', tone: 'green' },
  { label: '💊 Medications', tone: 'yellow' },
  { label: '📄 RAG Docs', tone: 'purple' },
  { label: '📥 PDF Reports', tone: 'pink' },
]

export function Landing() {
  return (
    <Shell
      sidebar={
        <>
          <p className="notice notice-info">
            Log in to access your personal dashboard, track vitals, and get tailored AI insights.
          </p>
          <a className="btn btn-primary" href={api.loginUrl}>
            🔗 Login with Google
          </a>
        </>
      }
    >
      <section className="hero">
        <h1>🏥 HealthCare AI Assistant</h1>
        <p className="muted">
          AI-powered health companion — chat, track vitals, manage meds &amp; get personalized insights.
        </p>
        <div className="pills">
          {FEATURES.map((f) => (
            <span key={f.label} className={`pill pill-${f.tone}`}>
              {f.label}
            </span>
          ))}
        </div>
      </section>

      <hr />

      <h3>💬 Try it now — Chat as Guest</h3>
      <p className="caption">
        Login with Google to unlock personalized insights, vitals tracking, and your private health history.
      </p>
      <ChatPanel />
    </Shell>
  )
}
