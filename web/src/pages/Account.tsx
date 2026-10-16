import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { CalendarX, Download, ShieldCheck, Trash2 } from 'lucide-react'
import { api } from '../api/client'
import { useAuth, useUser } from '../auth/AuthContext'
import { errorMessage, useToast } from '../components/Toast'
import { ConfirmDialog, Notice } from '../components/ui'
import { APP_NAME, CONTACT_EMAIL } from '../config'

export function Account() {
  const { userId, profile } = useUser()
  const { logout } = useAuth()
  const notify = useToast()
  const navigate = useNavigate()

  const [confirm, setConfirm] = useState<'calendar' | 'delete' | null>(null)
  const [busy, setBusy] = useState(false)

  async function disconnectCalendar() {
    setBusy(true)
    try {
      await api.disconnectCalendar(userId)
      notify('success', 'Google Calendar disconnected. Your HealthAgent reminders were removed from your calendar.')
      setConfirm(null)
    } catch (err) {
      notify('error', errorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  async function deleteAccount() {
    setBusy(true)
    try {
      await api.deleteAccount(userId)
      logout()
      navigate('/', { replace: true })
    } catch (err) {
      notify('error', errorMessage(err))
      setBusy(false)
    }
  }

  async function downloadReport() {
    try {
      await api.downloadHealthReport(userId)
    } catch (err) {
      notify('error', errorMessage(err))
    }
  }

  return (
    <>
      <section className="card" aria-labelledby="acct-google">
        <h2 id="acct-google">Signed in with Google</h2>
        <p>
          <strong>{profile.name || 'User'}</strong>
          <br />
          <span className="muted">{profile.email}</span>
        </p>
        <p className="caption">
          {APP_NAME} uses your name, email address and profile picture only to create and identify your account.
        </p>
      </section>

      <section className="card" aria-labelledby="acct-calendar">
        <h2 id="acct-calendar">Google Calendar</h2>
        <p>
          When you add a medication reminder, {APP_NAME} creates and deletes those reminder events in your Google
          Calendar. It does not read your other events. You can disconnect at any time: your {APP_NAME} reminders are
          removed from your calendar and Google access is revoked.
        </p>
        <button type="button" className="btn btn-secondary" onClick={() => setConfirm('calendar')}>
          <CalendarX className="icon" size={18} aria-hidden="true" />
          Disconnect Google Calendar
        </button>
        <p className="caption" style={{ marginTop: 12 }}>
          You can also review or remove access from your Google Account at{' '}
          <a href="https://myaccount.google.com/permissions" target="_blank" rel="noreferrer">
            myaccount.google.com/permissions
          </a>
          .
        </p>
      </section>

      <section className="card" aria-labelledby="acct-data">
        <h2 id="acct-data">Your data</h2>
        <p>
          Download a PDF copy of your health information, or read how we handle it in the{' '}
          <Link to="/privacy">Privacy Policy</Link>. To correct your data, edit it in the app. For any other request,
          email <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>.
        </p>
        <div className="row">
          <button type="button" className="btn btn-secondary" onClick={() => void downloadReport()}>
            <Download className="icon" size={18} aria-hidden="true" />
            Download my health report
          </button>
          <Link className="btn btn-ghost" to="/privacy">
            <ShieldCheck className="icon" size={18} aria-hidden="true" />
            Privacy Policy
          </Link>
        </div>
      </section>

      <section className="card" aria-labelledby="acct-delete">
        <h2 id="acct-delete">Delete account</h2>
        <Notice tone="warning">
          This permanently deletes your account, health profile, health logs, medications, dose history and uploaded
          documents. It cannot be undone.
        </Notice>
        <button type="button" className="btn btn-danger" onClick={() => setConfirm('delete')}>
          <Trash2 className="icon" size={18} aria-hidden="true" />
          Delete my account and data
        </button>
      </section>

      {confirm === 'calendar' && (
        <ConfirmDialog
          title="Disconnect Google Calendar?"
          confirmLabel="Disconnect"
          busy={busy}
          onConfirm={() => void disconnectCalendar()}
          onCancel={() => setConfirm(null)}
        >
          <p className="muted" style={{ margin: 0 }}>
            Your {APP_NAME} medication reminders will be deleted from your calendar. Your medications stay in {APP_NAME}.
          </p>
        </ConfirmDialog>
      )}
      {confirm === 'delete' && (
        <ConfirmDialog
          title="Delete your account?"
          confirmLabel="Delete everything"
          busy={busy}
          onConfirm={() => void deleteAccount()}
          onCancel={() => setConfirm(null)}
        >
          <p className="muted" style={{ margin: 0 }}>
            All of your data will be permanently deleted and you will be signed out.
          </p>
        </ConfirmDialog>
      )}
    </>
  )
}
