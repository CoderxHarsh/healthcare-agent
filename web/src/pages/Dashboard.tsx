import { useQuery } from '@tanstack/react-query'
import { healthLogsQuery, vitalsSummaryQuery } from '../api/queries'
import type { HealthLog } from '../api/types'
import { useUser } from '../auth/AuthContext'
import { changeSincePrevious, logsOfType, rangeStatus } from '../lib/metrics'

const VITALS = [
  { type: 'heart_rate', title: 'Heart Rate', unit: 'bpm', cardSuffix: '' },
  { type: 'blood_pressure', title: 'Blood Pressure', unit: '', cardSuffix: '' },
  { type: 'sleep', title: 'Sleep', unit: 'h', cardSuffix: 'h' },
  { type: 'weight', title: 'Weight', unit: 'kg', cardSuffix: '' },
]

const DOT_CLASS = { in: 'dot-green', out: 'dot-yellow', unknown: 'dot-gray' }
const DOT_TITLE = {
  in: 'Within the reference range',
  out: 'Outside the reference range',
  unknown: 'No reference range',
}

function VitalCard({ logs, vital }: { logs: HealthLog[]; vital: (typeof VITALS)[number] }) {
  const latest = logsOfType(logs, vital.type)[0]
  const change = changeSincePrevious(logs, vital.type, vital.unit)

  return (
    <div className="card">
      <div className="metric-title">{vital.title}</div>
      {latest ? (
        <>
          <div className="metric-value">
            {latest.value}
            {vital.cardSuffix}
          </div>
          {change && <div className="metric-change">{change}</div>}
        </>
      ) : (
        <div className="metric-empty">--</div>
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
            <span>{vital.title}</span>
            <span className="vitals-val">
              <span className={`dot ${DOT_CLASS[status]}`} title={DOT_TITLE[status]} />
              {latest ? latest.value : '--'} {vital.unit}
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
  if (query.isPending) text = '🔍 Analyzing your health data...'
  else if (query.isError) text = `Could not retrieve analysis. ${query.error.message}`
  else text = query.data.summary || 'Analysis unavailable.'

  return (
    <div className="card">
      <div className="metric-title">🤖 AI Analysis</div>
      <p className="ai-text">{text}</p>
      <div className="row">
        {!query.isPending && (
          <span className={`badge ${failed ? 'badge-error' : 'badge-success'}`}>
            {failed ? '⚠️ CHECK NEEDED' : '✅ GENERATED'}
          </span>
        )}
        <span className="badge badge-info">ML POWERED</span>
        <button
          type="button"
          className="btn btn-secondary btn-small"
          onClick={() => void query.refetch()}
          disabled={query.isFetching}
        >
          {query.isFetching ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>
    </div>
  )
}

export function Dashboard() {
  const { userId } = useUser()
  const logsQuery = useQuery(healthLogsQuery(userId, 90))
  const logs = logsQuery.data ?? []

  return (
    <>
      <h2>Dashboard</h2>
      <p className="muted">Overview of your vitals</p>

      {logsQuery.isError && (
        <p className="notice notice-error">⚠️ Could not load health data: {logsQuery.error.message}</p>
      )}
      {logsQuery.isPending && <p className="caption">Loading health data...</p>}

      <div className="grid-4">
        {VITALS.map((vital) => (
          <VitalCard key={vital.type} logs={logs} vital={vital} />
        ))}
      </div>

      <div className="grid-2">
        <VitalsSummaryCard logs={logs} />
        <AiAnalysisCard userId={userId} />
      </div>
    </>
  )
}
