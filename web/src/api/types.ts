export interface Profile {
  id: number
  email: string | null
  name: string | null
  is_onboarded: boolean
  age: number | null
  gender: string | null
  height_cm: number | null
  weight_kg: number | null
  health_conditions: string | null
  medications: string | null
  allergies: string | null
  fitness_level: string | null
  health_goals: string | null
  onboarded_at: string | null
}

export interface OnboardingPayload {
  age: number
  gender: string
  height_cm: number
  weight_kg: number
  health_conditions: string | null
  medications: string | null
  allergies: string | null
  fitness_level: string
  health_goals: string | null
}

export interface GoalsPayload {
  health_goals?: string
  weight_kg?: number
  fitness_level?: string
}

export interface HealthLog {
  id: number
  metric_type: string
  value: string
  unit: string | null
  notes: string | null
  created_at: string
  source: string
}

export interface HealthLogPayload {
  metric_type: string
  value: string
  unit: string
  notes?: string | null
  source: 'manual' | 'chatbot'
}

export interface ParsedMetric {
  metric_type: string
  value: string
  unit: string
}

export interface SummaryEntry {
  value: string
  unit: string | null
  timestamp: string
  notes: string | null
}

export type HealthSummary = Record<string, SummaryEntry[]>

export interface BulkImportResult {
  status: string
  message: string
  imported: number
  skipped: number
}

export interface Medication {
  id: number
  name: string
  dosage: string | null
  frequency: string
  time_of_day: string | null
  start_date: string | null
  end_date: string | null
  notes: string | null
  is_active: boolean
  has_calendar_event: boolean
}

export interface MedicationPayload {
  name: string
  dosage: string | null
  frequency: string
  time_of_day: string
  start_date: string
  end_date: string | null
  notes: string | null
}

export interface AddMedicationResult {
  status: string
  message: string
  medication_id: number
  calendar_event: string
}

export interface Adherence {
  total_medications: number
  period_days: number
  total_expected_doses: number
  taken: number
  skipped: number
  not_logged: number
  adherence_rate: number
}

export interface VitalsSummary {
  status: 'success' | 'error'
  summary: string
  generated_at?: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatPayload {
  message: string
  user_profile?: Profile | null
  health_logs?: HealthLog[] | null
  chat_history?: ChatMessage[]
}
