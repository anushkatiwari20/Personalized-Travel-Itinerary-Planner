import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { tripsAPI, prefsAPI, errorMessage } from '../services/api'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ArrowLeft, ArrowRight, Loader, MapPin, Calendar, Users, Sparkles, CheckCircle2, Globe,
  Waves, Mountain, UtensilsCrossed, Palmtree, Camera, Music, Landmark, Heart, Baby, Wallet, Plane,
} from 'lucide-react'
import TopBar from '../components/TopBar'

const STYLES = [
  { id: 'cultural', label: 'Cultural', icon: Landmark },
  { id: 'adventure', label: 'Adventure', icon: Mountain },
  { id: 'relaxed', label: 'Relaxed', icon: Palmtree },
  { id: 'luxury', label: 'Luxury', icon: Sparkles },
  { id: 'budget', label: 'Budget', icon: Wallet },
  { id: 'romantic', label: 'Romantic', icon: Heart },
  { id: 'family', label: 'Family', icon: Baby },
]
const INTERESTS = [
  { id: 'food', label: 'Food', icon: UtensilsCrossed },
  { id: 'history', label: 'History', icon: Landmark },
  { id: 'nature', label: 'Nature', icon: Mountain },
  { id: 'beaches', label: 'Beaches', icon: Waves },
  { id: 'art', label: 'Art', icon: Camera },
  { id: 'nightlife', label: 'Nightlife', icon: Music },
  { id: 'shopping', label: 'Shopping', icon: Globe },
  { id: 'wellness', label: 'Wellness', icon: Heart },
]
const PACES = [
  { id: 'relaxed', label: 'Relaxed', hint: '1–2 activities / day' },
  { id: 'moderate', label: 'Moderate', hint: '2–3 activities / day' },
  { id: 'fast', label: 'Fast', hint: '3–4 activities / day' },
]
const DIETS = ['Vegetarian', 'Vegan', 'Jain', 'Halal', 'Gluten-free', 'No seafood']

const todayPlus = (n) => {
  const d = new Date()
  d.setDate(d.getDate() + n)
  return d.toISOString().slice(0, 10)
}

export const CreateTrip = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [formData, setFormData] = useState({
    destination: '',
    start_date: todayPlus(7),
    end_date: todayPlus(10),
    travel_style: 'cultural',
    interests: ['food', 'history'],
    group_size: 1,
    pace: 'moderate',
    budget_per_day: 2000,
    dietary_restrictions: [],
    mobility_concerns: '',
    notes: '',
  })

  // Pre-fill from Explore ("Start Planning This Trip") and from saved preferences
  useEffect(() => {
    const raw = location.state?.prefill
    const KEYS = ['destination', 'start_date', 'end_date', 'travel_style', 'interests', 'group_size', 'pace', 'budget_per_day', 'dietary_restrictions', 'mobility_concerns', 'notes']
    const pre = raw ? Object.fromEntries(KEYS.filter((k) => raw[k] !== undefined && raw[k] !== null).map((k) => [k, raw[k]])) : null
    if (pre) setFormData((f) => ({ ...f, ...pre }))
    prefsAPI.get().then((p) => {
      if (!p) return
      setFormData((f) => ({
        ...f,
        travel_style: pre?.travel_style || p.travel_style || f.travel_style,
        interests: pre?.interests?.length ? pre.interests : p.interests?.length ? p.interests : f.interests,
        pace: pre?.pace || p.pace || f.pace,
        budget_per_day: pre?.budget_per_day || p.budget_per_day || f.budget_per_day,
        dietary_restrictions: pre?.dietary_restrictions || p.dietary_restrictions || [],
      }))
    }).catch(() => {})
  }, [location.state])

  const set = (k, v) => setFormData((f) => ({ ...f, [k]: v }))
  const toggle = (k, v) => setFormData((f) => ({ ...f, [k]: f[k].includes(v) ? f[k].filter((x) => x !== v) : [...f[k], v] }))

  const validateStep = () => {
    if (step === 1) {
      if (formData.destination.trim().length < 2) return 'Please enter a destination.'
      if (formData.end_date < formData.start_date) return 'End date must be after the start date.'
    }
    if (step === 2 && formData.interests.length === 0) return 'Pick at least one interest.'
    return ''
  }
  const next = () => {
    const e = validateStep()
    if (e) return setError(e)
    setError('')
    setStep((s) => Math.min(3, s + 1))
  }
  const back = () => { setError(''); setStep((s) => Math.max(1, s - 1)) }

  const submit = async () => {
    setError('')
    setLoading(true)
    try {
      const payload = {
        ...formData,
        group_size: Number(formData.group_size),
        budget_per_day: Number(formData.budget_per_day),
        mobility_concerns: formData.mobility_concerns || null,
        notes: formData.notes || null,
      }
      const trip = await tripsAPI.create(payload)
      navigate(`/trips/${trip.id}`, { state: { autoGenerate: true } })
    } catch (err) {
      setError(errorMessage(err, 'Could not create trip'))
      setLoading(false)
    }
  }

  const steps = ['Basics', 'Preferences', 'Logistics']

  return (
    <>
      <TopBar placeholder="Where to next?" />
      <div className="page" style={{ maxWidth: 820, margin: '0 auto' }}>
        <div className="stepper">
          {steps.map((label, i) => {
            const n = i + 1
            return (
              <React.Fragment key={label}>
                <div className={`step ${step === n ? 'active' : ''} ${step > n ? 'done' : ''}`}>
                  <div className="step-dot">{step > n ? <CheckCircle2 size={16} /> : n}</div>
                  {label.toUpperCase()}
                </div>
                {n < 3 && <div className={`step-line ${step > n ? 'done' : ''}`} />}
              </React.Fragment>
            )
          })}
        </div>

        <AnimatePresence mode="wait">
          <motion.div key={step} className="card card-pad" initial={{ opacity: 0, x: 24 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -24 }} transition={{ duration: 0.2 }} style={{ padding: 30 }}>
            {step === 1 && (
              <>
                <h2>Essential Details</h2>
                <p className="muted" style={{ marginTop: 4 }}>Tell us where and when you want to go.</p>
                <div className="divider" />
                <div className="field" style={{ marginBottom: 16 }}>
                  <label>Destination</label>
                  <div className="input-icon"><MapPin size={16} /><input className="input" placeholder="e.g. Hyderabad, Goa, Bali" value={formData.destination} onChange={(e) => set('destination', e.target.value)} autoFocus /></div>
                </div>
                <div className="grid grid-2">
                  <div className="field"><label>Start date</label><div className="input-icon"><Calendar size={16} /><input className="input" type="date" value={formData.start_date} onChange={(e) => set('start_date', e.target.value)} /></div></div>
                  <div className="field"><label>End date</label><div className="input-icon"><Calendar size={16} /><input className="input" type="date" min={formData.start_date} value={formData.end_date} onChange={(e) => set('end_date', e.target.value)} /></div></div>
                </div>
              </>
            )}

            {step === 2 && (
              <>
                <h2>Vibe & Interests</h2>
                <p className="muted" style={{ marginTop: 4 }}>Personalize your journey to match your soul.</p>
                <div className="divider" />
                <div className="field" style={{ marginBottom: 20 }}>
                  <label>Travel style</label>
                  <div className="vibe-grid" style={{ gridTemplateColumns: 'repeat(7, 1fr)' }}>
                    {STYLES.map(({ id, label, icon: Icon }) => (
                      <button key={id} type="button" className={`vibe ${formData.travel_style === id ? 'active' : ''}`} onClick={() => set('travel_style', id)}><Icon size={18} />{label}</button>
                    ))}
                  </div>
                </div>
                <div className="field" style={{ marginBottom: 20 }}>
                  <label>Interests (select any)</label>
                  <div className="row wrap" style={{ gap: 8 }}>
                    {INTERESTS.map(({ id, label, icon: Icon }) => (
                      <button key={id} type="button" className={`chip chip-btn ${formData.interests.includes(id) ? 'active' : ''}`} onClick={() => toggle('interests', id)}><Icon size={12} /> {label}</button>
                    ))}
                  </div>
                </div>
                <div className="field">
                  <label>Pace</label>
                  <div className="grid grid-3">
                    {PACES.map((p) => (
                      <button key={p.id} type="button" className={`vibe ${formData.pace === p.id ? 'active' : ''}`} style={{ alignItems: 'flex-start', padding: 14 }} onClick={() => set('pace', p.id)}>
                        <b style={{ fontSize: 14 }}>{p.label}</b><span style={{ fontWeight: 400 }}>{p.hint}</span>
                      </button>
                    ))}
                  </div>
                </div>
              </>
            )}

            {step === 3 && (
              <>
                <h2>Final Logistics</h2>
                <p className="muted" style={{ marginTop: 4 }}>The little things that make it perfect.</p>
                <div className="divider" />
                <div className="grid grid-2" style={{ marginBottom: 16 }}>
                  <div className="field"><label>Group size</label><div className="input-icon"><Users size={16} /><input className="input" type="number" min={1} max={50} value={formData.group_size} onChange={(e) => set('group_size', e.target.value)} /></div></div>
                  <div className="field"><label>Daily budget (INR, per person)</label><div className="input-icon"><span style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--muted)' }}>₹</span><input className="input" type="number" min={0} step={100} value={formData.budget_per_day} onChange={(e) => set('budget_per_day', e.target.value)} /></div></div>
                </div>
                <div className="field" style={{ marginBottom: 16 }}>
                  <label>Dietary restrictions</label>
                  <div className="row wrap" style={{ gap: 8 }}>
                    {DIETS.map((d) => <button key={d} type="button" className={`chip chip-btn ${formData.dietary_restrictions.includes(d) ? 'active' : ''}`} onClick={() => toggle('dietary_restrictions', d)}>{d}</button>)}
                  </div>
                </div>
                <div className="field" style={{ marginBottom: 16 }}>
                  <label>Mobility considerations</label>
                  <input className="input" placeholder="E.g. wheelchair access, avoid long treks…" value={formData.mobility_concerns} onChange={(e) => set('mobility_concerns', e.target.value)} />
                </div>
                <div className="field">
                  <label>Additional notes</label>
                  <textarea className="textarea" placeholder="E.g. travelling with kids, specific places you must visit, allergies…" value={formData.notes} onChange={(e) => set('notes', e.target.value)} />
                </div>
              </>
            )}

            {error && <div className="alert alert-error" style={{ marginTop: 18 }}>{error}</div>}

            <div className="row between" style={{ marginTop: 26 }}>
              <button type="button" className="btn btn-ghost" onClick={step === 1 ? () => navigate(-1) : back}><ArrowLeft size={16} /> {step === 1 ? 'Cancel' : 'Previous'}</button>
              {step < 3 ? (
                <button type="button" className="btn btn-primary" onClick={next}>Next Step <ArrowRight size={16} /></button>
              ) : (
                <button type="button" className="btn btn-accent" onClick={submit} disabled={loading}>
                  {loading ? <><Loader size={16} className="spin" /> Creating…</> : <><Sparkles size={16} /> Generate Itinerary</>}
                </button>
              )}
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </>
  )
}

export default CreateTrip
