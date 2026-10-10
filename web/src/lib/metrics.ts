import type { HealthLog } from '../api/types'

export function titleCase(snake: string): string {
  return snake
    .split('_')
    .filter(Boolean)
    .map((w) => w[0].toUpperCase() + w.slice(1))
    .join(' ')
}

export function formatDateTime(iso: string): string {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

export function todayIso(): string {
  const d = new Date()
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

/** HealthLog.value is free-form text ("75.5", "7 hours"), so pull out the first number. */
export function extractNumber(value: unknown): number | null {
  const match = /[-+]?\d*\.\d+|\d+/.exec(String(value))
  return match ? Number(match[0]) : null
}

export function parseBloodPressure(value: string): { systolic: number; diastolic: number } | null {
  const parts = value.split('/')
  if (parts.length !== 2) return null
  const systolic = extractNumber(parts[0])
  const diastolic = extractNumber(parts[1])
  return systolic && diastolic ? { systolic, diastolic } : null
}

/** Logs arrive newest-first from the API. */
export function logsOfType(logs: HealthLog[], metricType: string): HealthLog[] {
  return logs.filter((l) => l.metric_type === metricType)
}

function signed(n: number): string {
  const rounded = Math.round(n * 10) / 10
  return `${rounded > 0 ? '+' : ''}${rounded}`
}

/** Change between the two most recent readings of a metric; null when the values can't be compared. */
export function changeSincePrevious(logs: HealthLog[], metricType: string, unit: string): string | null {
  const [latest, previous] = logsOfType(logs, metricType)
  if (!latest) return null
  if (!previous) return 'Only one reading so far'

  if (metricType === 'blood_pressure') {
    const a = parseBloodPressure(latest.value)
    const b = parseBloodPressure(previous.value)
    if (!a || !b) return null
    const ds = a.systolic - b.systolic
    const dd = a.diastolic - b.diastolic
    if (ds === 0 && dd === 0) return 'No change since last reading'
    return `${signed(ds)}/${signed(dd)} since last reading`
  }

  const a = extractNumber(latest.value)
  const b = extractNumber(previous.value)
  if (a === null || b === null) return null
  const diff = a - b
  if (Math.abs(diff) < 0.05) return 'No change since last reading'
  return `${diff > 0 ? '↑' : '↓'} ${signed(diff)} ${unit} since last reading`
}

export type RangeStatus = 'in' | 'out' | 'unknown'

// Same reference ranges the backend uses in backend/health_analyzer.py (normal_ranges).
const RANGES: Record<string, [number, number]> = {
  heart_rate: [60, 100],
  sleep: [7, 9],
}
const BP_SYSTOLIC: [number, number] = [90, 120]
const BP_DIASTOLIC: [number, number] = [60, 80]

const within = (n: number, [min, max]: [number, number]) => n >= min && n <= max

export function rangeStatus(metricType: string, value: string): RangeStatus {
  if (metricType === 'blood_pressure') {
    const bp = parseBloodPressure(value)
    if (!bp) return 'unknown'
    return within(bp.systolic, BP_SYSTOLIC) && within(bp.diastolic, BP_DIASTOLIC) ? 'in' : 'out'
  }
  const range = RANGES[metricType]
  const n = extractNumber(value)
  if (!range || n === null) return 'unknown'
  return within(n, range) ? 'in' : 'out'
}

/** Average of each numeric series per calendar date, oldest first, for the trend charts. */
export function dailyMeans<K extends string>(
  logs: HealthLog[],
  metricType: string,
  toPoint: (log: HealthLog) => Record<K, number> | null,
): Array<{ date: string } & Record<K, number>> {
  const byDate = new Map<string, Array<Record<K, number>>>()
  for (const log of logsOfType(logs, metricType)) {
    const point = toPoint(log)
    if (!point) continue
    const date = log.created_at.split('T')[0]
    const bucket = byDate.get(date)
    if (bucket) bucket.push(point)
    else byDate.set(date, [point])
  }

  return [...byDate.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, points]) => {
      const keys = Object.keys(points[0]) as K[]
      const means = {} as Record<K, number>
      for (const key of keys) {
        const mean = points.reduce((sum, p) => sum + p[key], 0) / points.length
        means[key] = Math.round(mean * 10) / 10
      }
      return { date, ...means }
    })
}
