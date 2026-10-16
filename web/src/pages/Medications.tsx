import { useState, type FormEvent } from 'react'
import { keepPreviousData, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import { adherenceQuery, medicationsQuery } from '../api/queries'
import type { Medication } from '../api/types'
import { useUser } from '../auth/AuthContext'
import { Tabs } from '../components/Tabs'
import { CalendarCheck, CalendarX, Check, Clock, Plus, Repeat, SkipForward, Trash2, TrendingUp } from 'lucide-react'
import { ConfirmDialog, Notice } from '../components/ui'
import { errorMessage, useToast } from '../components/Toast'
import { titleCase, todayIso } from '../lib/metrics'

const FREQUENCIES = ['daily', 'twice_daily', 'weekly', 'as_needed']

function MedicationCard({ med, userId }: { med: Medication; userId: number }) {
  const queryClient = useQueryClient()
  const notify = useToast()
  const [busy, setBusy] = useState(false)
  const [confirming, setConfirming] = useState(false)

  async function run(action: () => Promise<unknown>, onDone: () => void) {
    setBusy(true)
    try {
      await action()
      await queryClient.invalidateQueries({ queryKey: ['medications', userId] })
      onDone()
    } catch (err) {
      notify('error', `${errorMessage(err)}`)
    } finally {
      setBusy(false)
    }
  }

  function handleRemove() {
    void run(
      () => api.removeMedication(med.id),
      () => {
        setConfirming(false)
        notify('success', `${med.name} removed.`)
      },
    )
  }

  return (
    <div className="card">
      <div className="med-head">
        <div>
          <span className="med-name">{med.name}</span>
          <span className="muted"> {med.dosage}</span>
        </div>
        {med.has_calendar_event ? (
          <span className="chip chip-ok">
            <CalendarCheck className="icon" size={14} aria-hidden="true" />
            Reminder set
          </span>
        ) : (
          <span className="chip chip-muted">
            <CalendarX className="icon" size={14} aria-hidden="true" />
            No reminder
          </span>
        )}
      </div>
      <div className="med-meta">
        <span>
          <Repeat className="icon" size={16} aria-hidden="true" />
          {titleCase(med.frequency)}
        </span>
        <span>
          <Clock className="icon" size={16} aria-hidden="true" />
          {med.time_of_day || 'N/A'}
        </span>
        <span>From {med.start_date}</span>
      </div>
      {med.notes && <div className="caption">{med.notes}</div>}

      <div className="grid-3">
        <button
          type="button"
          className="btn btn-success"
          disabled={busy}
          onClick={() =>
            void run(
              () => api.logMedication(med.id, todayIso(), 'taken'),
              () => notify('success', `${med.name} marked as taken!`),
            )
          }
        >
          <Check className="icon" size={16} aria-hidden="true" />
          Taken
        </button>
        <button
          type="button"
          className="btn btn-warning"
          disabled={busy}
          onClick={() =>
            void run(
              () => api.logMedication(med.id, todayIso(), 'skipped'),
              () => notify('warning', `${med.name} marked as skipped.`),
            )
          }
        >
          <SkipForward className="icon" size={16} aria-hidden="true" />
          Skipped
        </button>
        <button type="button" className="btn btn-secondary" disabled={busy} onClick={() => setConfirming(true)}>
          <Trash2 className="icon" size={16} aria-hidden="true" />
          Remove
        </button>
      </div>
      {confirming && (
        <ConfirmDialog
          title={`Remove ${med.name}?`}
          confirmLabel="Remove"
          busy={busy}
          onConfirm={handleRemove}
          onCancel={() => setConfirming(false)}
        >
          <p className="muted" style={{ margin: 0 }}>
            Its Google Calendar reminder will be deleted too.
          </p>
        </ConfirmDialog>
      )}
    </div>
  )
}

function MedicationsTab({ userId }: { userId: number }) {
  const query = useQuery(medicationsQuery(userId))
  // The backend can return the same medication twice; show each id once.
  const meds = [...new Map((query.data ?? []).map((m) => [m.id, m])).values()]

  return (
    <>
      <h2>Active medications</h2>
      {query.isPending && <p className="caption">Loading...</p>}
      {query.isError && <Notice tone="error">{query.error.message}</Notice>}
      {query.data && meds.length === 0 && (
        <Notice tone="info">
          No medications added yet. Add your first medication in the "Add Medication" tab.
        </Notice>
      )}
      {meds.map((med) => (
        <MedicationCard key={med.id} med={med} userId={userId} />
      ))}
    </>
  )
}

function AddMedicationTab({ userId }: { userId: number }) {
  const queryClient = useQueryClient()
  const notify = useToast()
  const [name, setName] = useState('')
  const [dosage, setDosage] = useState('')
  const [frequency, setFrequency] = useState(FREQUENCIES[0])
  const [time, setTime] = useState('08:00')
  const [start, setStart] = useState(todayIso)
  const [end, setEnd] = useState('')
  const [notes, setNotes] = useState('')
  const [saving, setSaving] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!name.trim()) {
      notify('error', 'Medication name is required.')
      return
    }
    setSaving(true)
    try {
      const result = await api.addMedication(userId, {
        name: name.trim(),
        dosage: dosage.trim() || null,
        frequency,
        time_of_day: time.trim(),
        start_date: start || todayIso(),
        end_date: end || null,
        notes: notes.trim() || null,
      })
      void queryClient.invalidateQueries({ queryKey: ['medications', userId] })
      notify('success', `${name.trim()} added successfully!`)
      if (result.calendar_event === 'created') {
        notify('info', 'Google Calendar reminder created! Check your calendar.')
      } else {
        notify('warning', 'Calendar reminder could not be created (login may need refresh).')
      }
      setName('')
      setDosage('')
      setNotes('')
    } catch (err) {
      notify('error', `${errorMessage(err)}`)
    } finally {
      setSaving(false)
    }
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <h2>Add new medication</h2>
      <p className="caption">
        A recurring reminder will be created in your Google Calendar for this medication. HealthAgent only creates and
        deletes the reminder events it adds; it does not read your other events.
      </p>
      <div className="grid-2">
        <label className="field">
          Medication name (required)
          <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Metformin" />
        </label>
        <label className="field">
          Time of day
          <input type="text" value={time} onChange={(e) => setTime(e.target.value)} />
          <span className="caption">Format: HH:MM (24hr). For twice daily, use e.g. 08:00,20:00</span>
        </label>
        <label className="field">
          Dosage
          <input type="text" value={dosage} onChange={(e) => setDosage(e.target.value)} placeholder="e.g. 500mg" />
        </label>
        <label className="field">
          Start Date
          <input type="date" value={start} onChange={(e) => setStart(e.target.value)} />
        </label>
        <label className="field">
          Frequency (required)
          <select value={frequency} onChange={(e) => setFrequency(e.target.value)}>
            {FREQUENCIES.map((f) => (
              <option key={f} value={f}>
                {titleCase(f)}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          End Date (optional)
          <input type="date" value={end} onChange={(e) => setEnd(e.target.value)} />
        </label>
      </div>
      <label className="field">
        Notes
        <textarea value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="e.g. Take with food" />
      </label>
      <button type="submit" className="btn btn-primary btn-block" disabled={saving}>
        <Plus className="icon" size={18} aria-hidden="true" />
        {saving ? 'Saving...' : 'Add medication and create reminder'}
      </button>
    </form>
  )
}

function AdherenceTab({ userId }: { userId: number }) {
  const [days, setDays] = useState(30)
  const query = useQuery({ ...adherenceQuery(userId, days), placeholderData: keepPreviousData })
  const stats = query.data

  return (
    <>
      <h2>Adherence report</h2>
      <label className="field">
        Report Period (days): {days}
        <input type="range" min={7} max={90} value={days} onChange={(e) => setDays(Number(e.target.value))} />
      </label>

      {query.isPending && <p className="caption">Loading...</p>}
      {query.isError && (
        <Notice tone="error">Could not load adherence report: {query.error.message}</Notice>
      )}
      {stats &&
        (stats.total_medications === 0 ? (
          <Notice tone="info">
            No adherence data yet. Add a medication and use the "My Medications" tab to log doses.
          </Notice>
        ) : (
          <div className="card">
            <div className="metric-title">
              <TrendingUp className="icon" size={16} aria-hidden="true" />
              Overall adherence (last {stats.period_days} days)
            </div>
            <div className="metric-value">{Math.round(stats.adherence_rate)}%</div>
            <div className={stats.adherence_rate >= 80 ? 'metric-good' : 'metric-warn'}>
              {stats.adherence_rate >= 80 ? 'Great, keep it up.' : 'Needs improvement'}
            </div>
            <progress max={100} value={Math.min(stats.adherence_rate, 100)} />
            <div className="stat-row">
              <span>Taken: {stats.taken}</span>
              <span>Skipped: {stats.skipped}</span>
              <span>Not logged: {stats.not_logged}</span>
              <span>of {stats.total_expected_doses} expected doses</span>
            </div>
          </div>
        ))}
    </>
  )
}

export function Medications() {
  const { userId } = useUser()

  return (
    <>
      <Tabs
        tabs={[
          { id: 'list', label: 'My Medications', content: <MedicationsTab userId={userId} /> },
          { id: 'add', label: 'Add Medication', content: <AddMedicationTab userId={userId} /> },
          { id: 'adherence', label: 'Adherence Report', content: <AdherenceTab userId={userId} /> },
        ]}
      />
    </>
  )
}
