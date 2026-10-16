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
import { Droplets, Flower2, Footprints, Moon, Pencil, Salad, Save, Scale, Target, type LucideIcon } from 'lucide-react'
import { errorMessage, useToast } from '../components/Toast'
import { Notice } from '../components/ui'
import { dailyMeans, extractNumber, parseBloodPressure } from '../lib/metrics'

const FITNESS_LEVELS = ['sedentary', 'light', 'moderate', 'active', 'very active']

const GOAL_ICONS: Array<[icon: LucideIcon, keywords: string[]]> = [
  [Scale, ['weight', 'kg', 'lose', 'gain']],
  [Footprints, ['run', 'walk', 'exercise', 'gym', 'fitness', 'cardio']],
  [Moon, ['sleep', 'rest']],
  [Salad, ['diet', 'eat', 'nutrition', 'calorie']],
  [Flower2, ['stress', 'meditat', 'mental', 'anxiety']],
  [Droplets, ['water', 'hydrat']],
]

function GoalIcon({ goal }: { goal: string }) {
  const lower = goal.toLowerCase()
  const Icon = GOAL_ICONS.find(([, keywords]) => keywords.some((k) => lower.includes(k)))?.[0] ?? Target
  return <Icon className="icon" size={20} aria-hidden="true" />
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
      notify('success', 'Goals saved.')
    } catch (err) {
      notify('error', errorMessage(err))
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
        <Save className="icon" size={18} aria-hidden="true" />
        {saving ? 'Saving...' : 'Save goals'}
      </button>
    </form>
  )
}

const AXIS = { stroke: '#5E6B72', fontSize: 12 }
const TOOLTIP_STYLE = { background: '#FFFFFF', border: '1px solid #E6E1DA', borderRadius: 8 }

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
            <CartesianGrid stroke="#E6E1DA" strokeDasharray="0" vertical={false} />
            <XAxis dataKey="date" {...AXIS} />
            <YAxis domain={['auto', 'auto']} {...AXIS} />
            <Tooltip contentStyle={TOOLTIP_STYLE} />
            <Line type="monotone" dataKey="Weight (kg)" stroke="#2F7F86" strokeWidth={2} isAnimationActive={false} />
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
            <CartesianGrid stroke="#E6E1DA" strokeDasharray="0" vertical={false} />
            <XAxis dataKey="date" {...AXIS} />
            <YAxis {...AXIS} />
            <Tooltip contentStyle={TOOLTIP_STYLE} cursor={{ fill: 'rgba(47,127,134,0.06)' }} />
            <Bar dataKey="Sleep (hours)" fill="#5AA9AE" radius={[4, 4, 0, 0]} isAnimationActive={false} />
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
          <CartesianGrid stroke="#E6E1DA" strokeDasharray="0" vertical={false} />
          <XAxis dataKey="date" {...AXIS} />
          <YAxis domain={['auto', 'auto']} {...AXIS} />
          <Tooltip contentStyle={TOOLTIP_STYLE} />
          <Legend />
          <Line type="monotone" dataKey="Systolic (High)" stroke="#D9776B" strokeWidth={2} isAnimationActive={false} />
          <Line type="monotone" dataKey="Diastolic (Low)" stroke="#6B8FC4" strokeWidth={2} isAnimationActive={false} />
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
      <div className="grid-goals">
        {goals.length ? (
          <div className="card">
            <div className="metric-title">Active Goals</div>
            {goals.map((goal, i) => (
              <div key={i} className="goal-row">
                <span className="goal-icon">
                  <GoalIcon goal={goal} />
                </span>
                <span>{goal}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="card card-empty">
            <div className="goal-icon">
              <Target className="icon" size={24} aria-hidden="true" />
            </div>
            <div>No health goals set yet. Add your first goal using the form.</div>
          </div>
        )}

        <details className="card" open={goals.length === 0}>
          <summary>
            <Pencil className="icon" size={16} aria-hidden="true" />
            Edit goals
          </summary>
          {/* Remount when the saved profile changes so the form shows the stored values. */}
          <GoalsForm
            key={`${profile.health_goals}|${profile.weight_kg}|${profile.fitness_level}`}
            userId={userId}
            profile={profile}
          />
        </details>
      </div>

      <hr />
      <h2>Progress Trends</h2>

      {logsQuery.isPending && <p className="caption" role="status">Loading health logs...</p>}
      {logsQuery.isError && (
        <Notice tone="error">Error loading health logs: {logsQuery.error.message}</Notice>
      )}
      {logsQuery.data &&
        (logsQuery.data.length === 0 ? (
          <Notice tone="info">
            No health logs available yet. Chat with the assistant to start tracking your vitals!
            <ul>
              <li>'I weigh 75kg today'</li>
              <li>'I slept 7 hours'</li>
              <li>'My blood pressure is 120/80'</li>
            </ul>
          </Notice>
        ) : (
          <Trends logs={logsQuery.data} />
        ))}
    </>
  )
}
