import type { ReactNode } from 'react'
import { Link, Navigate, NavLink, Outlet, useLocation } from 'react-router-dom'
import { Activity, Download, LayoutDashboard, LogOut, MessageCircle, Pill, Target, type LucideIcon } from 'lucide-react'
import { useState } from 'react'
import { api } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import { errorMessage, useToast } from './Toast'
import { Brand, BrandMark } from './ui'

const NAV: Array<{ to: string; label: string; Icon: LucideIcon }> = [
  { to: '/chat', label: 'Chat', Icon: MessageCircle },
  { to: '/dashboard', label: 'Dashboard', Icon: LayoutDashboard },
  { to: '/goals', label: 'Goals', Icon: Target },
  { to: '/wellness', label: 'Wellness', Icon: Activity },
  { to: '/medications', label: 'Medications', Icon: Pill },
]

const PAGE_TITLES: Record<string, { title: string; caption: string }> = {
  '/chat': { title: 'Chat', caption: 'Ask about your health, symptoms, or medications' },
  '/dashboard': { title: 'Dashboard', caption: 'Overview of your vitals' },
  '/goals': { title: 'Health Goals', caption: 'Track and update your personal health objectives' },
  '/wellness': { title: 'Your Wellness Tracker', caption: 'Log, review and import your health metrics' },
  '/medications': {
    title: 'Medication Manager',
    caption: 'Track your prescriptions, log doses, and set Google Calendar reminders',
  },
  '/account': { title: 'Account & Data', caption: 'Manage your connected services and your data' },
}

function initials(name: string | null | undefined): string {
  const parts = (name ?? '').trim().split(/\s+/).filter(Boolean)
  if (parts.length === 0) return 'U'
  return (parts[0][0] + (parts.length > 1 ? parts[parts.length - 1][0] : '')).toUpperCase()
}

export function LegalLinks() {
  return (
    <div className="sidebar-footer">
      <Link to="/terms">Terms of Service</Link>
      <Link to="/privacy">Privacy Policy</Link>
    </div>
  )
}

/** Two-column page frame shared by the guest landing page and the signed-in app. */
export function Shell({
  sidebar,
  children,
  guest = false,
}: {
  sidebar: ReactNode
  children: ReactNode
  guest?: boolean
}) {
  return (
    <div className="shell">
      <a className="skip-link" href="#main">
        Skip to main content
      </a>
      <aside className={`sidebar${guest ? ' sidebar-guest' : ''}`}>
        <Brand />
        {sidebar}
        <LegalLinks />
      </aside>
      <main className="main" id="main" tabIndex={-1}>
        {children}
      </main>
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
  if (status === 'loading')
    return (
      <FullPageMessage>
        <BrandMark size={48} />
        <p role="status">Loading your profile...</p>
      </FullPageMessage>
    )
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
  const { pathname } = useLocation()
  const notify = useToast()
  const [downloading, setDownloading] = useState(false)

  if (userId === null || !profile) return <Navigate to="/" replace />
  if (!profile.is_onboarded) return <Navigate to="/onboarding" replace />

  const page = PAGE_TITLES[pathname]
  const name = profile.name || 'User'

  return (
    <div className="shell">
      <a className="skip-link" href="#main">
        Skip to main content
      </a>
      <aside className="sidebar">
        <Brand />
        <nav className="nav" aria-label="Main">
          {NAV.map(({ to, label, Icon }) => (
            <NavLink key={to} to={to} className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`} title={label}>
              <Icon className="icon" size={20} aria-hidden="true" />
              <span className="nav-label">{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="user-chip">
            <span className="avatar" aria-hidden="true">
              {initials(name)}
            </span>
            <span className="user-chip-text">
              <strong>{name}</strong>
              <span className="caption">Signed in</span>
            </span>
            <button type="button" className="btn btn-ghost btn-small" onClick={logout} aria-label="Log out" title="Log out">
              <LogOut className="icon" size={16} aria-hidden="true" />
            </button>
          </div>
          <div className="sidebar-footer">
            <Link to="/account">Account &amp; data</Link>
            <Link to="/terms">Terms of Service</Link>
            <Link to="/privacy">Privacy Policy</Link>
          </div>
        </div>
      </aside>

      <main className="main" id="main" tabIndex={-1}>
        <div className="mobile-head">
          <Brand />
          <button type="button" className="btn btn-secondary btn-small" onClick={logout}>
            <LogOut className="icon" size={14} aria-hidden="true" />
            Log out
          </button>
        </div>
        <header className="topbar">
          <div>
            {page && (
              <>
                <h1>{page.title}</h1>
                <p className="muted">{page.caption}</p>
              </>
            )}
          </div>
          <button
            type="button"
            className="btn btn-secondary"
            disabled={downloading}
            onClick={async () => {
              setDownloading(true)
              try {
                await api.downloadHealthReport(userId)
              } catch (err) {
                notify('error', errorMessage(err))
              } finally {
                setDownloading(false)
              }
            }}
          >
            <Download className="icon" size={18} aria-hidden="true" />
            {downloading ? 'Preparing...' : 'PDF Report'}
          </button>
        </header>
        <Outlet />
      </main>

      <nav className="tabbar" aria-label="Main">
        {NAV.map(({ to, label, Icon }) => (
          <NavLink key={to} to={to} className={({ isActive }) => (isActive ? 'active' : undefined)}>
            <Icon className="icon" size={22} aria-hidden="true" />
            {label}
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
