import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, CheckCircle2, Gauge, HeartPulse, Loader2, Moon, RefreshCw, Scale, Sparkles, type LucideIcon } from 'lucide-react'
import { healthLogsQuery, vitalsSummaryQuery } from '../api/queries'
import type { HealthLog } from '../api/types'
import { useUser } from '../auth/AuthContext'
import { Notice, StatusChip, StatusIcon } from '../components/ui'
import { changeSincePrevious, logsOfType, rangeStatus } from '../lib/metrics'

interface Vital {
  type: string
  title: string
  unit: string
  Icon: LucideIcon
}

const VITALS: Vital[] = [
  { type: 'heart_rate', title: 'Heart Rate', unit: 'bpm', Icon: HeartPulse },
  { type: 'blood_pressure', title: 'Blood Pressure', unit: 'mmHg', Icon: Gauge },
  { type: 'sleep', title: 'Sleep', unit: 'h', Icon: Moon },
  { type: 'weight', title: 'Weight', unit: 'kg', Icon: Scale },
]

function greeting(name: string | null): string {
  const hour = new Date().getHours()
  const part = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening'
  const first = (name ?? '').trim().split(/\s+/)[0]
  return first ? `${part}, ${first}` : part
}

function VitalCard({ logs, vital }: { logs: HealthLog[]; vital: Vital }) {
  const latest = logsOfType(logs, vital.type)[0]
  const change = changeSincePrevious(logs, vital.type, vital.unit)
  const status = latest ? rangeStatus(vital.type, latest.value) : null

  return (
    <div className="card">
      <div className="metric-head">
        <div className="metric-title">{vital.title}</div>
        {status && <StatusChip status={status} />}
      </div>
      {latest ? (
        <>
          <div className="metric-value">
            {latest.value}
            <span className="metric-unit">{vital.unit}</span>
          </div>
          {change && <div className="metric-change">{change}</div>}
        </>
      ) : (
        <>
          <div className="metric-empty">--</div>
          <div className="metric-change">No reading yet</div>
        </>
      )}
    </div>
  )
}

function VitalsSummaryCard({ logs }: { logs: HealthLog[] }) {
  return (
    <div className="card">
      <div className="metric-title">Vitals Summary</div>
      {VITALS.map((vital) => {
        const latest = logsOfType(logs, vital.type)[0]
        const status = latest ? rangeStatus(vital.type, latest.value) : 'unknown'
        return (
          <div key={vital.type} className="vitals-row">
            <span className="vitals-label">
              <vital.Icon className="icon" size={18} aria-hidden="true" color="var(--primary)" />
              {vital.title}
            </span>
            <span className="vitals-val">
              <StatusIcon status={status} />
              <span>
                {latest ? latest.value : '--'} <span className="metric-unit">{vital.unit}</span>
              </span>
            </span>
          </div>
        )
      })}
    </div>
  )
}

function AiAnalysisCard({ userId }: { userId: number }) {
  const query = useQuery(vitalsSummaryQuery(userId))
  const failed = query.isError || query.data?.status === 'error'

  let text: string
  if (query.isPending) text = 'Analyzing your health data...'
  else if (query.isError) text = `Could not retrieve analysis. ${query.error.message}`
  else text = query.data.summary || 'Analysis unavailable.'

  return (
    <div className="card ai-card">
      <div className="ai-card-head">
        <span className="avatar avatar-ai" aria-hidden="true">
          <Sparkles size={16} />
        </span>
        <div className="metric-title">AI Analysis</div>
      </div>
      <p className="ai-text" role="status">
        {text}
      </p>
      <div className="row">
        {!query.isPending && (
          <span className={`chip ${failed ? 'chip-warn' : 'chip-ok'}`}>
            {failed ? (
              <AlertTriangle className="icon" size={14} aria-hidden="true" />
            ) : (
              <CheckCircle2 className="icon" size={14} aria-hidden="true" />
            )}
            {failed ? 'Check needed' : 'Generated'}
          </span>
        )}
        <span className="badge badge-info">AI-generated</span>
        <button
          type="button"
          className="btn btn-secondary btn-small"
          onClick={() => void query.refetch()}
          disabled={query.isFetching}
        >
          {query.isFetching ? (
            <Loader2 className="icon spin" size={14} aria-hidden="true" />
          ) : (
            <RefreshCw className="icon" size={14} aria-hidden="true" />
          )}
          {query.isFetching ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>
      <p className="caption" style={{ margin: '12px 0 0' }}>
        General information, not medical advice.
      </p>
    </div>
  )
}

export function Dashboard() {
  const { userId, profile } = useUser()
  const logsQuery = useQuery(healthLogsQuery(userId, 90))
  const logs = logsQuery.data ?? []

  return (
    <>
      <h2 style={{ marginBottom: 16 }}>{greeting(profile.name)}</h2>

      {logsQuery.isError && <Notice tone="error">Could not load health data: {logsQuery.error.message}</Notice>}
      {logsQuery.isPending && (
        <p className="caption" role="status">
          Loading health data...
        </p>
      )}
      {!logsQuery.isPending && !logsQuery.isError && logs.length === 0 && (
        <Notice tone="info">
          No readings yet. Add one in Wellness, or tell the chat something like "my BP is 120/80".
        </Notice>
      )}

      <div className="grid-4">
        {VITALS.map((vital) => (
          <VitalCard key={vital.type} logs={logs} vital={vital} />
        ))}
      </div>

      <div className="grid-2">
        <VitalsSummaryCard logs={logs} />
        <AiAnalysisCard userId={userId} />
      </div>

      <p className="caption">
        Reference ranges: Heart rate 60-100 bpm · Sleep 7-9 h · Blood pressure 90-120 / 60-80 mmHg.
      </p>
    </>
  )
}
