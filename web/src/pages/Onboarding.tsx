import { useState, type FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { Check, Lock } from 'lucide-react'
import { useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import { useUser } from '../auth/AuthContext'
import { BrandMark, Notice } from '../components/ui'
import { APP_NAME, MIN_AGE } from '../config'
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
          <Check className="icon check" size={16} aria-hidden="true" />
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
  const [agreed, setAgreed] = useState(false)

  if (profile.is_onboarded) return <Navigate to="/chat" replace />

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const ageNum = Number(age)
    const heightNum = Number(height)
    const weightNum = Number(weight)
    if (ageNum && ageNum < MIN_AGE) {
      setError(`${APP_NAME} is for adults aged ${MIN_AGE} or older.`)
      return
    }
    if (!ageNum || !heightNum || !weightNum) {
      setError('Please fill in all required fields (Age, Gender, Height, Weight, Fitness Level)')
      return
    }

    if (!agreed) {
      setError('Please confirm that you agree to the Terms of Service and Privacy Policy to continue.')
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
      <div className="row" style={{ justifyContent: 'center', marginBottom: 20 }}>
        <BrandMark />
        <strong style={{ color: 'var(--text)', fontSize: '1.125rem' }}>{APP_NAME}</strong>
      </div>
      <h1 style={{ textAlign: 'center' }}>Complete your health profile</h1>
      <p className="muted" style={{ textAlign: 'center' }}>
        Help us know you better. This information helps us personalize your health guidance.
      </p>

      <form className="card form" onSubmit={handleSubmit} noValidate>
        <section className="form-section" aria-labelledby="sec-about">
          <h2 id="sec-about">About you</h2>
          <div className="grid-2">
            <label className="field">
              Age (required)
              <input type="number" min={18} max={120} value={age} onChange={(e) => setAge(e.target.value)} />
            </label>
            <label className="field">
              Gender (required)
              <select value={gender} onChange={(e) => setGender(e.target.value)}>
                {GENDERS.map((g) => (
                  <option key={g}>{g}</option>
                ))}
              </select>
            </label>
            <label className="field">
              Height in cm (required)
              <input type="number" min={50} max={250} value={height} onChange={(e) => setHeight(e.target.value)} />
            </label>
            <label className="field">
              Weight in kg (required)
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
        </section>

        <section className="form-section" aria-labelledby="sec-background">
          <h2 id="sec-background">Health background</h2>
          <CheckboxGroup
            legend="Existing conditions (optional, select all that apply)"
            options={CONDITIONS}
            selected={conditions}
            onChange={setConditions}
          />
          <label className="field">
            Current medications (optional)
            <textarea
              value={medications}
              onChange={(e) => setMedications(e.target.value)}
              placeholder="List your medications, e.g., Aspirin, Metformin, etc."
            />
          </label>
          <label className="field">
            Allergies (optional)
            <textarea
              value={allergies}
              onChange={(e) => setAllergies(e.target.value)}
              placeholder="List any known allergies, medications or food"
            />
          </label>
        </section>

        <section className="form-section" aria-labelledby="sec-goals">
          <h2 id="sec-goals">Lifestyle and goals</h2>
          <label className="field">
            Fitness level (required)
            <select value={fitness} onChange={(e) => setFitness(e.target.value)}>
              {FITNESS_LEVELS.map((f) => (
                <option key={f}>{f}</option>
              ))}
            </select>
          </label>
          <CheckboxGroup legend="Health goals (optional)" options={GOALS} selected={goals} onChange={setGoals} />
        </section>

        <section className="form-section" aria-labelledby="sec-consent">
          <h2 id="sec-consent">Your privacy</h2>
          <p className="privacy-note">
            <Lock className="icon" size={16} aria-hidden="true" />
            Your information is private and used only to personalize your experience.
          </p>
          <label className="checkbox" style={{ alignItems: 'flex-start', borderRadius: 12, padding: '12px 16px' }}>
            <input type="checkbox" checked={agreed} onChange={(e) => setAgreed(e.target.checked)} />
            <Check className="icon check" size={16} aria-hidden="true" style={{ marginTop: 3 }} />
            <span>
              I am 18 or older and I agree to the <Link to="/terms" target="_blank">Terms of Service</Link> and{' '}
              <Link to="/privacy" target="_blank">Privacy Policy</Link>. I understand that the health information I enter
              is processed by AI services to answer my questions.
            </span>
          </label>
        </section>

        {error && <Notice tone="error">{error}</Notice>}

        <button type="submit" className="btn btn-primary btn-block" disabled={saving}>
          {saving ? 'Saving...' : 'Save and continue'}
        </button>
      </form>
    </div>
  )
}
