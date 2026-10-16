import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { ApiError, getSessionToken, onUnauthorized, setSessionToken } from '../api/client'
import { profileQuery } from '../api/queries'
import type { Profile } from '../api/types'

const STORAGE_KEY = 'healthagent.user_id'

type AuthStatus = 'guest' | 'loading' | 'error' | 'ready'

interface AuthState {
  status: AuthStatus
  userId: number | null
  profile: Profile | null
  error: string | null
  retry: () => void
  logout: () => void
}

const AuthContext = createContext<AuthState | null>(null)

function readStored(): number | null {
  try {
    const id = Number(localStorage.getItem(STORAGE_KEY))
    return Number.isInteger(id) && id > 0 ? id : null
  } catch {
    return null
  }
}

function writeStored(id: number | null) {
  try {
    if (id === null) localStorage.removeItem(STORAGE_KEY)
    else localStorage.setItem(STORAGE_KEY, String(id))
  } catch {
    // Storage unavailable (private mode): the session just won't survive a refresh.
  }
}

/**
 * The backend's /auth/callback redirects here with ?user_id=..&token=..
 * Take both from the URL once, remember them, and clean the address bar.
 */
function initialUserId(): number | null {
  const params = new URLSearchParams(window.location.search)
  const fromUrl = Number(params.get('user_id'))
  const tokenFromUrl = params.get('token')
  if (Number.isInteger(fromUrl) && fromUrl > 0 && tokenFromUrl) {
    writeStored(fromUrl)
    setSessionToken(tokenFromUrl)
    window.history.replaceState(null, '', window.location.pathname)
    return fromUrl
  }
  // A remembered id without a session token (an old session) can't call the API: start as a guest.
  return getSessionToken() ? readStored() : null
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()
  const [userId, setUserId] = useState<number | null>(initialUserId)

  const query = useQuery({
    ...profileQuery(userId ?? 0),
    enabled: userId !== null,
    retry: (failures, err) => !(err instanceof ApiError && err.status === 404) && failures < 2,
  })

  const logout = useCallback(() => {
    writeStored(null)
    setSessionToken(null)
    setUserId(null)
    queryClient.clear()
  }, [queryClient])

  // An expired or rejected session token signs the user out.
  useEffect(() => {
    onUnauthorized(logout)
    return () => onUnauthorized(null)
  }, [logout])

  // A stored id that no longer exists on the backend is a dead session.
  const notFound = query.error instanceof ApiError && query.error.status === 404
  useEffect(() => {
    if (notFound) logout()
  }, [notFound, logout])

  const value = useMemo<AuthState>(() => {
    let status: AuthStatus
    if (userId === null) status = 'guest'
    else if (query.data) status = 'ready'
    else if (query.isError) status = 'error'
    else status = 'loading'

    return {
      status,
      userId,
      profile: query.data ?? null,
      error: query.error ? query.error.message : null,
      retry: () => void query.refetch(),
      logout,
    }
  }, [userId, query.data, query.isError, query.error, query.refetch, logout])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}

/** For pages rendered behind the route guard, where a signed-in user is guaranteed. */
export function useUser(): { userId: number; profile: Profile } {
  const { userId, profile } = useAuth()
  if (userId === null || !profile) throw new Error('useUser must be used on an authenticated route')
  return { userId, profile }
}
