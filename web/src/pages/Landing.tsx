import { Link } from 'react-router-dom'
import { FileText, HeartPulse, KeyRound, MessageCircle, Pill, FileDown } from 'lucide-react'
import { api } from '../api/client'
import { ChatPanel } from '../components/ChatPanel'
import { Shell } from '../components/Layout'
import { APP_NAME } from '../config'

const FEATURES = [
  { label: 'AI Chat', tone: 'blue', Icon: MessageCircle },
  { label: 'Vitals', tone: 'green', Icon: HeartPulse },
  { label: 'Medications', tone: 'yellow', Icon: Pill },
  { label: 'Your documents', tone: 'purple', Icon: FileText },
  { label: 'PDF Reports', tone: 'pink', Icon: FileDown },
]

export function Landing() {
  return (
    <Shell
      guest
      sidebar={
        <>
          <div className="guest-copy">
            <p className="notice notice-info">
              Log in to access your personal dashboard, track vitals, and get tailored AI insights.
            </p>
          </div>
          <a className="btn btn-primary" href={api.loginUrl}>
            <KeyRound className="icon" size={18} aria-hidden="true" />
            <span className="nav-label">Continue with Google</span>
          </a>
        </>
      }
    >
      <section className="hero">
        <h1>Your AI health companion.</h1>
        <p className="lead">
          {APP_NAME} is a personal health companion: chat about your health, track vitals, manage medications and get
          personalized insights.
        </p>
        <div className="pills">
          {FEATURES.map(({ label, tone, Icon }) => (
            <span key={label} className={`pill pill-${tone}`}>
              <Icon className="icon" size={16} aria-hidden="true" />
              {label}
            </span>
          ))}
        </div>
      </section>

      <hr />

      <section aria-labelledby="google-use">
        <h2 id="google-use">How {APP_NAME} uses your Google account</h2>
        <p>
          You sign in with Google. We use your name, email address and profile picture only to create and identify your
          account. If you add a medication reminder, {APP_NAME} asks for permission to create and delete those reminder
          events in your Google Calendar. We never read your other calendar events, and we never sell your data. Read
          the <Link to="/privacy">Privacy Policy</Link> and <Link to="/terms">Terms of Service</Link>.
        </p>
      </section>

      <hr />

      <h2>Try it now, chat as a guest</h2>
      <p className="caption">
        Log in with Google to unlock personalized insights, vitals tracking, and your private health history.
      </p>
      <ChatPanel />
    </Shell>
  )
}
