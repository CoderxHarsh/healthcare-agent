import type { ReactNode } from 'react'
import { Link, Navigate, NavLink, Outlet } from 'react-router-dom'
import { api } from '../api/client'
import { useAuth } from '../auth/AuthContext'

const NAV = [
  { to: '/chat', label: 'Chat' },
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/goals', label: 'Goals' },
  { to: '/wellness', label: 'Wellness' },
  { to: '/medications', label: 'Medications' },
]

function Brand() {
  return (
    <div className="brand">
      <div className="brand-name">🏥 HealthAgent</div>
      <div className="brand-sub">AI Health Monitor</div>
    </div>
  )
}

function LegalLinks() {
  return (
    <div className="sidebar-footer">
      <Link to="/terms">📜 Terms of Service</Link>
      <Link to="/privacy">🔒 Privacy Policy</Link>
    </div>
  )
}

/** Two-column page frame shared by the guest landing page and the signed-in app. */
export function Shell({ sidebar, children }: { sidebar: ReactNode; children: ReactNode }) {
  return (
    <div className="shell">
      <aside className="sidebar">
        <Brand />
        {sidebar}
        <LegalLinks />
      </aside>
      <main className="main">{children}</main>
    </div>
  )
}

export function FullPageMessage({ children }: { children: ReactNode }) {
  return <div className="full-page">{children}</div>
}

/** Blocks signed-out visitors and waits for the profile before rendering any app page. */
export function RequireAuth() {
  const { status, error, retry, logout } = useAuth()

  if (status === 'guest') return <Navigate to="/" replace />
  if (status === 'loading') return <FullPageMessage>Loading your profile...</FullPageMessage>
  if (status === 'error') {
    return (
      <FullPageMessage>
        <p>{error}</p>
        <div className="row">
          <button type="button" className="btn btn-primary" onClick={retry}>
            Try again
          </button>
          <button type="button" className="btn btn-secondary" onClick={logout}>
            Log out
          </button>
        </div>
      </FullPageMessage>
    )
  }
  return <Outlet />
}

export function AppLayout() {
  const { userId, profile, logout } = useAuth()

  if (userId === null || !profile) return <Navigate to="/" replace />
  if (!profile.is_onboarded) return <Navigate to="/onboarding" replace />

  return (
    <Shell
      sidebar={
        <>
          <nav className="nav" aria-label="Main">
            {NAV.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) => `btn ${isActive ? 'btn-primary' : 'btn-secondary'}`}
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
          <div className="signed-in">
            <span className="muted">Signed in as</span>
            <strong>{profile.name || 'User'}</strong>
          </div>
          <button type="button" className="btn btn-secondary" onClick={logout}>
            Logout
          </button>
        </>
      }
    >
      <header className="topbar">
        <h1>🏥 HealthCare AI Assistant</h1>
        <a className="btn btn-secondary" href={api.healthReportUrl(userId)} target="_blank" rel="noreferrer">
          📥 PDF Report
        </a>
      </header>
      <Outlet />
    </Shell>
  )
}
