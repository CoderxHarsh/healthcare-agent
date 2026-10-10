import { lazy, Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './auth/AuthContext'
import { ChatProvider } from './chat/ChatContext'
import { AppLayout, RequireAuth } from './components/Layout'
import { Chat } from './pages/Chat'
import { Dashboard } from './pages/Dashboard'
import { Landing } from './pages/Landing'
import { Privacy, Terms } from './pages/Legal'
import { Medications } from './pages/Medications'
import { Onboarding } from './pages/Onboarding'
import { Wellness } from './pages/Wellness'

// The charting library is most of the bundle, so load it only when Goals is opened.
const Goals = lazy(() => import('./pages/Goals').then((m) => ({ default: m.Goals })))

function Home() {
  const { status } = useAuth()
  return status === 'guest' ? <Landing /> : <Navigate to="/chat" replace />
}

export function App() {
  const { userId } = useAuth()

  return (
    // Keyed by user so logging in or out starts a fresh conversation.
    <ChatProvider key={userId ?? 'guest'}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/terms" element={<Terms />} />
        <Route path="/privacy" element={<Privacy />} />
        <Route element={<RequireAuth />}>
          <Route path="/onboarding" element={<Onboarding />} />
          <Route element={<AppLayout />}>
            <Route path="/chat" element={<Chat />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route
              path="/goals"
              element={
                <Suspense fallback={<p className="caption">Loading...</p>}>
                  <Goals />
                </Suspense>
              }
            />
            <Route path="/wellness" element={<Wellness />} />
            <Route path="/medications" element={<Medications />} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </ChatProvider>
  )
}
