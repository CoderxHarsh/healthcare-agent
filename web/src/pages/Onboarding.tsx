import { useState, type FormEvent } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import { useUser } from '../auth/AuthContext'
import { errorMessage } from '../components/Toast'

const GENDERS = ['Male', 'Female', 'Other', 'Prefer not to say']
const FITNESS_LEVELS = ['Sedentary', 'Light', 'Moderate', 'Active', 'Very Active']
const CONDITIONS = [
  'Diabetes',
  'Hypertension (High Blood Pressure)',
  'Heart Disease',
  'Asthma',
  'Thyroid',
  'Arthritis',
  'Depression/Anxiety',
  'None',
  'Other',
]
const GOALS = [
  'Weight Loss',
  'Weight Gain',
  'Build Muscle',
  'Improve Endurance',
  'Reduce Stress',
  'Better Sleep',
  'General Wellness',
  'Manage Disease',
]

function CheckboxGroup({
  legend,
  options,
  selected,
  onChange,
}: {
  legend: string
  options: string[]
  selected: string[]
  onChange: (next: string[]) => void
}) {
  return (
    <fieldset className="field checkbox-group">
      <legend>{legend}</legend>
      {options.map((option) => (
        <label key={option} className="checkbox">
          <input
            type="checkbox"
            checked={selected.includes(option)}
            onChange={(e) =>
              onChange(e.target.checked ? [...selected, option] : selected.filter((s) => s !== option))
            }
          />
          {option}
        </label>
      ))}
    </fieldset>
  )
}

export function Onboarding() {
  const { userId, profile } = useUser()
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  const [age, setAge] = useState('')
  const [gender, setGender] = useState(GENDERS[0])
  const [height, setHeight] = useState('')
  const [weight, setWeight] = useState('')
  const [conditions, setConditions] = useState<string[]>([])
  const [medications, setMedications] = useState('')
  const [allergies, setAllergies] = useState('')
  const [fitness, setFitness] = useState(FITNESS_LEVELS[0])
  const [goals, setGoals] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  if (profile.is_onboarded) return <Navigate to="/chat" replace />

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const ageNum = Number(age)
    const heightNum = Number(height)
    const weightNum = Number(weight)
    if (!ageNum || !heightNum || !weightNum) {
      setError('Please fill in all required fields (Age, Gender, Height, Weight, Fitness Level)')
      return
    }

    setError(null)
    setSaving(true)
    try {
      await api.saveOnboarding(userId, {
        age: ageNum,
        gender,
        height_cm: heightNum,
        weight_kg: weightNum,
        health_conditions: conditions.length ? conditions.join(', ') : null,
        medications: medications.trim() || null,
        allergies: allergies.trim() || null,
        fitness_level: fitness,
        health_goals: goals.length ? goals.join(', ') : null,
      })
      await api.completeOnboarding(userId)
      await queryClient.invalidateQueries({ queryKey: ['profile', userId] })
      navigate('/chat', { replace: true })
    } catch (err) {
      setError(errorMessage(err))
      setSaving(false)
    }
  }

  return (
    <div className="page-narrow">
      <h1>🎯 Complete Your Health Profile</h1>
      <hr />
      <h3>Help us know you better!</h3>
      <p className="muted">
        This information helps us provide personalized health advice and recommendations.
      </p>

      <form className="card form" onSubmit={handleSubmit}>
        <div className="grid-2">
          <label className="field">
            Age *
            <input type="number" min={1} max={120} value={age} onChange={(e) => setAge(e.target.value)} />
          </label>
          <label className="field">
            Gender *
            <select value={gender} onChange={(e) => setGender(e.target.value)}>
              {GENDERS.map((g) => (
                <option key={g}>{g}</option>
              ))}
            </select>
          </label>
          <label className="field">
            Height (cm) *
            <input type="number" min={50} max={250} value={height} onChange={(e) => setHeight(e.target.value)} />
          </label>
          <label className="field">
            Weight (kg) *
            <input
              type="number"
              min={20}
              max={300}
              step="0.1"
              value={weight}
              onChange={(e) => setWeight(e.target.value)}
            />
          </label>
        </div>

        <CheckboxGroup
          legend="Health Conditions (select all that apply)"
          options={CONDITIONS}
          selected={conditions}
          onChange={setConditions}
        />

        <label className="field">
          Current Medications (if any)
          <textarea
            value={medications}
            onChange={(e) => setMedications(e.target.value)}
            placeholder="List your medications, e.g., Aspirin, Metformin, etc."
          />
        </label>

        <label className="field">
          Allergies (if any)
          <textarea
            value={allergies}
            onChange={(e) => setAllergies(e.target.value)}
            placeholder="List any known allergies, medications or food"
          />
        </label>

        <label className="field">
          Current Fitness Level *
          <select value={fitness} onChange={(e) => setFitness(e.target.value)}>
            {FITNESS_LEVELS.map((f) => (
              <option key={f}>{f}</option>
            ))}
          </select>
        </label>

        <CheckboxGroup legend="Health Goals" options={GOALS} selected={goals} onChange={setGoals} />

        {error && <p className="notice notice-error">❌ {error}</p>}

        <button type="submit" className="btn btn-primary btn-block" disabled={saving}>
          {saving ? 'Saving...' : '✅ Complete Onboarding'}
        </button>
      </form>
    </div>
  )
}
