import { useState, type FormEvent, type ReactNode } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { api } from '../api/client'
import { healthLogsQuery } from '../api/queries'
import type { GoalsPayload, HealthLog, Profile } from '../api/types'
import { useUser } from '../auth/AuthContext'
import { errorMessage, useToast } from '../components/Toast'
import { dailyMeans, extractNumber, parseBloodPressure } from '../lib/metrics'

const FITNESS_LEVELS = ['sedentary', 'light', 'moderate', 'active', 'very active']

const GOAL_ICONS: Array<[icon: string, keywords: string[]]> = [
  ['⚖️', ['weight', 'kg', 'lose', 'gain']],
  ['🏃', ['run', 'walk', 'exercise', 'gym', 'fitness', 'cardio']],
  ['😴', ['sleep', 'rest']],
  ['🥗', ['diet', 'eat', 'nutrition', 'calorie']],
  ['🧘', ['stress', 'meditat', 'mental', 'anxiety']],
  ['💧', ['water', 'hydrat']],
]

function goalIcon(goal: string): string {
  const lower = goal.toLowerCase()
  return GOAL_ICONS.find(([, keywords]) => keywords.some((k) => lower.includes(k)))?.[0] ?? '🎯'
}

function parseGoals(text: string): string[] {
  return text
    .replace(/\n/g, ',')
    .split(',')
    .map((g) => g.trim())
    .filter(Boolean)
}

function GoalsForm({ userId, profile }: { userId: number; profile: Profile }) {
  const queryClient = useQueryClient()
  const notify = useToast()
  const currentFitness = profile.fitness_level?.toLowerCase() ?? ''

  const [goals, setGoals] = useState(profile.health_goals ?? '')
  const [weight, setWeight] = useState(profile.weight_kg != null ? String(profile.weight_kg) : '')
  const [fitness, setFitness] = useState(FITNESS_LEVELS.includes(currentFitness) ? currentFitness : 'moderate')
  const [saving, setSaving] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const payload: GoalsPayload = { health_goals: goals, fitness_level: fitness }
    const weightNum = Number(weight)
    if (weight.trim() && weightNum > 0) payload.weight_kg = weightNum

    setSaving(true)
    try {
      await api.updateGoals(userId, payload)
      await queryClient.invalidateQueries({ queryKey: ['profile', userId] })
      notify('success', '✅ Goals saved!')
    } catch (err) {
      notify('error', `❌ ${errorMessage(err)}`)
    } finally {
      setSaving(false)
    }
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <label className="field">
        Your Goals
        <textarea
          value={goals}
          onChange={(e) => setGoals(e.target.value)}
          placeholder="e.g. Lose 5kg, Run 5km, Sleep 8 hours daily"
        />
        <span className="caption">Separate multiple goals with commas</span>
      </label>
      <label className="field">
        Target Weight (kg)
        <input
          type="number"
          min={30}
          max={300}
          step="0.5"
          value={weight}
          onChange={(e) => setWeight(e.target.value)}
        />
      </label>
      <label className="field">
        Fitness Level
        <select value={fitness} onChange={(e) => setFitness(e.target.value)}>
          {FITNESS_LEVELS.map((f) => (
            <option key={f}>{f}</option>
          ))}
        </select>
      </label>
      <button type="submit" className="btn btn-primary btn-block" disabled={saving}>
        {saving ? 'Saving...' : '💾 Save Goals'}
      </button>
    </form>
  )
}

const AXIS = { stroke: '#64748B', fontSize: 12 }
const TOOLTIP_STYLE = { background: '#171A21', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }

function ChartCard({ title, empty, children }: { title: string; empty: string | null; children: ReactNode }) {
  return (
    <div>
      <div className="metric-title">{title}</div>
      {empty ? (
        <p className="caption">{empty}</p>
      ) : (
        <div className="chart">
          <ResponsiveContainer width="100%" height="100%">
            {children}
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}

function Trends({ logs }: { logs: HealthLog[] }) {
  const single = (key: string) => (log: HealthLog) => {
    const n = extractNumber(log.value)
    return n === null ? null : { [key]: n }
  }
  const weight = dailyMeans(logs, 'weight', single('Weight (kg)'))
  const sleep = dailyMeans(logs, 'sleep', single('Sleep (hours)'))
  const bp = dailyMeans(logs, 'blood_pressure', (log) => {
    const reading = parseBloodPressure(log.value)
    return reading ? { 'Systolic (High)': reading.systolic, 'Diastolic (Low)': reading.diastolic } : null
  })

  return (
    <>
      <div className="grid-2">
        <ChartCard
          title="Weight Trend"
          empty={
            weight.length
              ? null
              : "No weight data logged recently. Tell the chatbot 'I weigh 70kg today' to see your chart!"
          }
        >
          <LineChart data={weight}>
            <CartesianGrid stroke="rgba(255,255,255,0.06)" />
            <XAxis dataKey="date" {...AXIS} />
            <YAxis domain={['auto', 'auto']} {...AXIS} />
            <Tooltip contentStyle={TOOLTIP_STYLE} />
            <Line type="monotone" dataKey="Weight (kg)" stroke="#20A4F3" strokeWidth={2} isAnimationActive={false} />
          </LineChart>
        </ChartCard>

        <ChartCard
          title="Sleep Consistency"
          empty={
            sleep.length
              ? null
              : "No sleep data logged recently. Tell the chatbot 'I slept 7 hours' to track your rest!"
          }
        >
          <BarChart data={sleep}>
            <CartesianGrid stroke="rgba(255,255,255,0.06)" />
            <XAxis dataKey="date" {...AXIS} />
            <YAxis {...AXIS} />
            <Tooltip contentStyle={TOOLTIP_STYLE} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
            <Bar dataKey="Sleep (hours)" fill="#20A4F3" radius={[4, 4, 0, 0]} isAnimationActive={false} />
          </BarChart>
        </ChartCard>
      </div>

      <ChartCard
        title="Blood Pressure Trend (mmHg)"
        empty={
          bp.length
            ? null
            : "No blood pressure data logged recently. Tell the chatbot 'My BP is 120/80' to track it!"
        }
      >
        <LineChart data={bp}>
          <CartesianGrid stroke="rgba(255,255,255,0.06)" />
          <XAxis dataKey="date" {...AXIS} />
          <YAxis domain={['auto', 'auto']} {...AXIS} />
          <Tooltip contentStyle={TOOLTIP_STYLE} />
          <Legend />
          <Line type="monotone" dataKey="Systolic (High)" stroke="#EF4444" strokeWidth={2} isAnimationActive={false} />
          <Line type="monotone" dataKey="Diastolic (Low)" stroke="#3B82F6" strokeWidth={2} isAnimationActive={false} />
        </LineChart>
      </ChartCard>
    </>
  )
}

export function Goals() {
  const { userId, profile } = useUser()
  const logsQuery = useQuery(healthLogsQuery(userId, 90))
  const goals = parseGoals(profile.health_goals ?? '')

  return (
    <>
      <h2>🎯 Health Goals</h2>
      <p className="muted">Track and update your personal health objectives</p>
      <hr />

      <div className="grid-goals">
        {goals.length ? (
          <div className="card">
            <div className="metric-title">Active Goals</div>
            {goals.map((goal, i) => (
              <div key={i} className="goal-row">
                <span className="goal-icon">{goalIcon(goal)}</span>
                <span>{goal}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="card card-empty">
            <div className="goal-icon">🎯</div>
            <div>No health goals set yet. Add your first goal →</div>
          </div>
        )}

        <details className="card" open={goals.length === 0}>
          <summary>✏️ Edit Goals</summary>
          {/* Remount when the saved profile changes so the form shows the stored values. */}
          <GoalsForm
            key={`${profile.health_goals}|${profile.weight_kg}|${profile.fitness_level}`}
            userId={userId}
            profile={profile}
          />
        </details>
      </div>

      <hr />
      <h3>📈 Progress Trends</h3>

      {logsQuery.isPending && <p className="caption">📊 Loading health logs...</p>}
      {logsQuery.isError && (
        <p className="notice notice-error">❌ Error loading health logs: {logsQuery.error.message}</p>
      )}
      {logsQuery.data &&
        (logsQuery.data.length === 0 ? (
          <div className="notice notice-info">
            📝 No health logs available yet. Chat with the assistant to start tracking your vitals!
            <ul>
              <li>'I weigh 75kg today'</li>
              <li>'I slept 7 hours'</li>
              <li>'My blood pressure is 120/80'</li>
            </ul>
          </div>
        ) : (
          <Trends logs={logsQuery.data} />
        ))}
    </>
  )
}
