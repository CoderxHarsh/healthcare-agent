import { useState, type FormEvent } from 'react'
import { keepPreviousData, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import { healthLogsQuery, healthSummaryQuery } from '../api/queries'
import { useUser } from '../auth/AuthContext'
import { Tabs } from '../components/Tabs'
import { errorMessage, useToast } from '../components/Toast'
import { formatDateTime, titleCase } from '../lib/metrics'

const FILTERS = ['All Metrics', 'Blood Pressure', 'Weight', 'Heart Rate', 'Blood Sugar', 'Sleep', 'Exercise']

const UNITS: Record<string, string> = {
  blood_pressure: 'mmHg',
  weight: 'kg',
  heart_rate: 'bpm',
  blood_sugar: 'mg/dL',
  sleep: 'hours',
  exercise: 'minutes',
  temperature: '°C',
}

function DaysSlider({ label, value, onChange }: { label: string; value: number; onChange: (n: number) => void }) {
  return (
    <label className="field">
      {label}: {value}
      <input type="range" min={1} max={90} value={value} onChange={(e) => onChange(Number(e.target.value))} />
    </label>
  )
}

function LogsTab({ userId }: { userId: number }) {
  const [filter, setFilter] = useState(FILTERS[0])
  const [days, setDays] = useState(30)
  const metricType = filter === FILTERS[0] ? undefined : filter.toLowerCase().replace(/ /g, '_')
  const query = useQuery({ ...healthLogsQuery(userId, days, metricType), placeholderData: keepPreviousData })

  return (
    <>
      <h3>Health Metrics History</h3>
      <div className="grid-2">
        <label className="field">
          Filter by Metric
          <select value={filter} onChange={(e) => setFilter(e.target.value)}>
            {FILTERS.map((f) => (
              <option key={f}>{f}</option>
            ))}
          </select>
        </label>
        <DaysSlider label="Show last N days" value={days} onChange={setDays} />
      </div>

      {query.isPending && <p className="caption">Loading...</p>}
      {query.isError && <p className="notice notice-error">❌ Error fetching logs: {query.error.message}</p>}
      {query.data &&
        (query.data.length === 0 ? (
          <p className="notice notice-info">📭 No metrics logged yet. Add one in the "Add Metric" tab!</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Metric</th>
                  <th>Value</th>
                  <th>Notes</th>
                </tr>
              </thead>
              <tbody>
                {query.data.map((log) => (
                  <tr key={log.id}>
                    <td>{formatDateTime(log.created_at)}</td>
                    <td>{titleCase(log.metric_type)}</td>
                    <td>
                      {log.value} {log.unit}
                    </td>
                    <td>{log.notes || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))}
    </>
  )
}

function AddMetricTab({ userId }: { userId: number }) {
  const queryClient = useQueryClient()
  const notify = useToast()
  const [metricType, setMetricType] = useState('blood_pressure')
  const [value, setValue] = useState('')
  const [notes, setNotes] = useState('')
  const [saving, setSaving] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!value.trim()) {
      notify('error', '❌ Please enter a value')
      return
    }
    setSaving(true)
    try {
      await api.createHealthLog(userId, {
        metric_type: metricType,
        value: value.trim(),
        unit: UNITS[metricType] ?? '',
        notes: notes.trim() || null,
        source: 'manual',
      })
      void queryClient.invalidateQueries({ queryKey: ['health-logs', userId] })
      void queryClient.invalidateQueries({ queryKey: ['vitals-summary', userId] })
      setValue('')
      setNotes('')
      notify('success', '✅ Metric saved successfully!')
    } catch (err) {
      notify('error', `❌ ${errorMessage(err)}`)
    } finally {
      setSaving(false)
    }
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <h3>Add Health Metric</h3>
      <div className="grid-2">
        <label className="field">
          Metric Type
          <select value={metricType} onChange={(e) => setMetricType(e.target.value)}>
            {Object.keys(UNITS).map((m) => (
              <option key={m} value={m}>
                {titleCase(m)}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          Value in {UNITS[metricType]} (e.g., 120/80, 75.5, 8)
          <input type="text" value={value} onChange={(e) => setValue(e.target.value)} />
        </label>
      </div>
      <label className="field">
        Notes (optional)
        <textarea value={notes} onChange={(e) => setNotes(e.target.value)} />
      </label>
      <button type="submit" className="btn btn-primary btn-block" disabled={saving}>
        {saving ? 'Saving...' : '💾 Save Metric'}
      </button>
    </form>
  )
}

function SummaryTab({ userId }: { userId: number }) {
  const [days, setDays] = useState(30)
  const query = useQuery({ ...healthSummaryQuery(userId, days), placeholderData: keepPreviousData })
  const groups = Object.entries(query.data ?? {})

  return (
    <>
      <h3>Health Summary</h3>
      <DaysSlider label="Summary period (days)" value={days} onChange={setDays} />

      {query.isPending && <p className="caption">Loading...</p>}
      {query.isError && <p className="notice notice-error">❌ Error: {query.error.message}</p>}
      {query.data && groups.length === 0 && (
        <p className="notice notice-info">📭 No metrics logged yet in this period.</p>
      )}
      {groups.map(([metricType, entries]) => (
        <details key={metricType} className="card">
          <summary>
            📊 {titleCase(metricType)} ({entries.length} entries)
          </summary>
          {entries.slice(0, 5).map((entry, i) => (
            <div key={i} className="summary-row">
              <span className="caption">{formatDateTime(entry.timestamp)}</span>
              <span>
                <strong>{entry.value}</strong> {entry.unit}
              </span>
              <span className="caption">{entry.notes && <em>{entry.notes}</em>}</span>
            </div>
          ))}
        </details>
      ))}
    </>
  )
}

function BulkImportTab({ userId }: { userId: number }) {
  const queryClient = useQueryClient()
  const notify = useToast()
  const [file, setFile] = useState<File | null>(null)
  const [busy, setBusy] = useState(false)

  async function handleImport() {
    if (!file) return
    setBusy(true)
    try {
      const result = await api.bulkImportHealthLogs(userId, file)
      notify(result.skipped > 0 ? 'warning' : 'success', result.message)
      void queryClient.invalidateQueries({ queryKey: ['health-logs', userId] })
      void queryClient.invalidateQueries({ queryKey: ['vitals-summary', userId] })
    } catch (err) {
      notify('error', `❌ ${errorMessage(err)}`)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="form">
      <h3>📥 Bulk Import Health Logs</h3>
      <p>Upload a CSV, JSON, or XML file containing your historical health logs.</p>
      <p className="notice notice-info">
        Expected columns/keys: <code>metric_type</code>, <code>value</code>, <code>unit</code> (optional),{' '}
        <code>date</code> (optional).
      </p>
      <label className="field">
        Upload file
        <input type="file" accept=".csv,.json,.xml" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
      </label>
      {file && (
        <button type="button" className="btn btn-primary btn-block" onClick={handleImport} disabled={busy}>
          {busy ? 'Processing file...' : '🚀 Process Import'}
        </button>
      )}
    </div>
  )
}

export function Wellness() {
  const { userId } = useUser()

  return (
    <>
      <h2>📊 Your Wellness Tracker</h2>
      <Tabs
        tabs={[
          { id: 'logs', label: '📈 View Logs', content: <LogsTab userId={userId} /> },
          { id: 'add', label: '➕ Add Metric', content: <AddMetricTab userId={userId} /> },
          { id: 'summary', label: '📋 Summary', content: <SummaryTab userId={userId} /> },
          { id: 'import', label: '📥 Bulk Import', content: <BulkImportTab userId={userId} /> },
        ]}
      />
    </>
  )
}
