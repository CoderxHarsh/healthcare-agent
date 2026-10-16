import type {
  AddMedicationResult,
  Adherence,
  BulkImportResult,
  ChatPayload,
  GoalsPayload,
  HealthLog,
  HealthLogPayload,
  HealthSummary,
  Medication,
  MedicationPayload,
  OnboardingPayload,
  ParsedMetric,
  Profile,
  VitalsSummary,
} from './types'

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000').replace(/\/+$/, '')

/** status is 0 when the request never got a response (network failure or timeout). */
export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

type Params = Record<string, string | number | boolean | null | undefined>

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PATCH' | 'DELETE'
  json?: unknown
  form?: FormData
  params?: Params
  timeoutMs?: number
}

function detailMessage(body: unknown): string | null {
  if (!body || typeof body !== 'object' || !('detail' in body)) return null
  const detail = (body as { detail: unknown }).detail
  if (typeof detail === 'string') return detail
  // FastAPI validation errors: [{ loc, msg, type }, ...]
  if (Array.isArray(detail)) {
    return detail
      .map((d) => (d && typeof d === 'object' && 'msg' in d ? String((d as { msg: unknown }).msg) : String(d)))
      .join('; ')
  }
  return null
}

async function request<T>(path: string, opts: RequestOptions = {}): Promise<T> {
  const { method = 'GET', json, form, params, timeoutMs = 15_000 } = opts

  const qs = new URLSearchParams()
  for (const [key, value] of Object.entries(params ?? {})) {
    if (value !== null && value !== undefined) qs.set(key, String(value))
  }
  const query = qs.toString()
  const url = `${API_BASE_URL}${path}${query ? `?${query}` : ''}`

  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeoutMs)

  let res: Response
  try {
    res = await fetch(url, {
      method,
      headers: json !== undefined ? { 'Content-Type': 'application/json' } : undefined,
      body: json !== undefined ? JSON.stringify(json) : form,
      signal: controller.signal,
    })
  } catch {
    throw new ApiError(
      0,
      controller.signal.aborted
        ? 'The request timed out. The server may be waking up — please try again in a minute.'
        : `Cannot connect to the backend at ${API_BASE_URL}. Is the server running?`,
    )
  } finally {
    clearTimeout(timer)
  }

  const body: unknown = await res.json().catch(() => null)
  if (!res.ok) {
    throw new ApiError(res.status, detailMessage(body) ?? `Request failed (status ${res.status})`)
  }
  return body as T
}

function fileForm(file: File): FormData {
  const form = new FormData()
  form.append('file', file, file.name)
  return form
}

export const api = {
  /** Backend route that starts the Google OAuth flow and redirects back with ?user_id=... */
  loginUrl: `${API_BASE_URL}/login`,

  healthReportUrl: (userId: number) => `${API_BASE_URL}/export/health-report/${userId}`,

  // ── User ──
  getProfile: (userId: number) =>
    request<{ profile: Profile }>(`/user/${userId}/profile`).then((r) => r.profile),

  saveOnboarding: (userId: number, data: OnboardingPayload) =>
    request<unknown>(`/user/${userId}/onboarding`, { method: 'POST', json: data }),

  completeOnboarding: (userId: number) =>
    request<unknown>(`/user/${userId}/complete-onboarding`, { method: 'POST' }),

  updateGoals: (userId: number, data: GoalsPayload) =>
    request<unknown>(`/user/${userId}/goals`, { method: 'PATCH', json: data }),

  getVitalsSummary: (userId: number) =>
    request<VitalsSummary>(`/user/${userId}/vitals-summary`, { timeoutMs: 45_000 }),

  // ── Health logs ──
  getHealthLogs: (userId: number, opts: { days: number; metricType?: string }) =>
    request<{ logs: HealthLog[] }>(`/health-logs/${userId}`, {
      params: { days: opts.days, metric_type: opts.metricType },
    }).then((r) => r.logs ?? []),

  createHealthLog: (userId: number, data: HealthLogPayload) =>
    request<unknown>(`/health-logs/${userId}`, { method: 'POST', json: data }),

  getHealthSummary: (userId: number, days: number) =>
    request<{ summary: HealthSummary }>(`/health-logs/${userId}/summary`, { params: { days } }).then(
      (r) => r.summary ?? {},
    ),

  bulkImportHealthLogs: (userId: number, file: File) =>
    request<BulkImportResult>(`/health-logs/${userId}/upload`, {
      method: 'POST',
      form: fileForm(file),
      timeoutMs: 60_000,
    }),

  // ── Medications ──
  getMedications: (userId: number) =>
    request<{ medications: Medication[] }>(`/medications/${userId}`, { params: { active_only: true } }).then(
      (r) => r.medications ?? [],
    ),

  addMedication: (userId: number, data: MedicationPayload) =>
    request<AddMedicationResult>(`/medications/${userId}`, { method: 'POST', json: data, timeoutMs: 30_000 }),

  logMedication: (medicationId: number, scheduledDate: string, status: 'taken' | 'skipped') =>
    request<unknown>(`/medications/${medicationId}/log`, {
      method: 'POST',
      json: { scheduled_date: scheduledDate, status },
    }),

  removeMedication: (medicationId: number) =>
    request<unknown>(`/medications/${medicationId}`, { method: 'DELETE', timeoutMs: 30_000 }),

  getAdherence: (userId: number, days: number) =>
    request<Adherence>(`/medications/${userId}/adherence`, { params: { days } }),

  // ── Chat & RAG ──
  chat: (payload: ChatPayload) =>
    request<{ response?: string }>('/chat', { method: 'POST', json: payload, timeoutMs: 60_000 }),

  parseMetrics: (text: string) =>
    request<{ metrics: ParsedMetric[] }>('/parse-metrics', { method: 'POST', json: { text } }).then(
      (r) => r.metrics ?? [],
    ),

  uploadDocument: (userId: number, file: File) =>
    request<{ file: string; chunks_indexed: number }>(`/rag/upload/${userId}`, {
      method: 'POST',
      form: fileForm(file),
      timeoutMs: 120_000,
    }),
}
