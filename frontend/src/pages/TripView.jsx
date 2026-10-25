import React, { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { tripsAPI, savedAPI, errorMessage } from '../services/api'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ArrowLeft, Loader, MapPin, Calendar, Users, Zap, Download, Edit2, Navigation, Hotel, Coffee,
  Sun, Moon, Plane, Clock, Briefcase, Sparkles, RefreshCw, Share2, Bookmark, Check,
} from 'lucide-react'
import { Sidebar } from '../components/Sidebar'
import { TopBar } from '../components/TopBar'
import { getPlaceImage } from '../utils/placeImages'
import { formatDate, formatINR } from '../utils/auth'

const VIBES = ['relaxed', 'adventure', 'luxury', 'budget', 'cultural', 'romantic', 'family']

export const TripView = () => {
  const { tripId } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const [trip, setTrip] = useState(null)
  const [itinerary, setItinerary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')
  const [toast, setToast] = useState('')
  const [regenDay, setRegenDay] = useState('')
  const [feedback, setFeedback] = useState('')
  const [vibe, setVibe] = useState('')
  const [savedNames, setSavedNames] = useState(new Set())

  const flash = (msg) => { setToast(msg); setTimeout(() => setToast(''), 2500) }

  const load = useCallback(async () => {
    try {
      const t = await tripsAPI.get(tripId)
      setTrip(t)
      if (t.has_itinerary) setItinerary(await tripsAPI.itinerary(tripId))
      const saved = await savedAPI.list().catch(() => [])
      setSavedNames(new Set(saved.map((s) => s.name)))
    } catch (e) {
      setError(errorMessage(e))
    } finally {
      setLoading(false)
    }
  }, [tripId])

  useEffect(() => { load() }, [load])

  const generate = async () => {
    setGenerating(true)
    setError('')
    try {
      setItinerary(await tripsAPI.generate(tripId))
      setTrip((t) => ({ ...t, has_itinerary: true, status: 'generated' }))
      flash('Itinerary generated')
    } catch (e) {
      setError(errorMessage(e, 'Generation failed'))
    } finally {
      setGenerating(false)
    }
  }

  // Auto-generate right after creating the trip
  useEffect(() => {
    if (!loading && trip && !trip.has_itinerary && location.state?.autoGenerate) generate()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loading])

  const regenerate = async () => {
    setGenerating(true)
    setError('')
    try {
      setItinerary(await tripsAPI.regenerate(tripId, { day: regenDay ? Number(regenDay) : null, feedback: feedback || null, travel_style: vibe || null }))
      setFeedback('')
      flash(regenDay ? `Day ${regenDay} regenerated` : 'Itinerary regenerated')
    } catch (e) {
      setError(errorMessage(e, 'Regeneration failed'))
    } finally {
      setGenerating(false)
    }
  }

  const download = async () => {
    const md = await tripsAPI.exportMarkdown(tripId)
    const blob = new Blob([md], { type: 'text/markdown' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `${trip.destination.replace(/\s+/g, '-')}-itinerary.md`
    a.click()
    URL.revokeObjectURL(a.href)
    flash('Downloaded')
  }

  const share = async () => {
    const text = `${trip.destination} itinerary (${formatDate(trip.start_date)} – ${formatDate(trip.end_date)})\n${itinerary?.summary || ''}\n${window.location.href}`
    if (navigator.share) {
      try { await navigator.share({ title: `${trip.destination} trip`, text, url: window.location.href }) } catch { /* cancelled */ }
    } else {
      await navigator.clipboard.writeText(text)
      flash('Summary copied to clipboard')
    }
  }

  const savePlace = async (text, slot) => {
    const name = text.split(' - ')[0].split(' – ')[0].trim().slice(0, 120)
    if (savedNames.has(name)) return
    await savedAPI.add({ name, description: text, category: slot === 'dining' ? 'dining' : 'attraction', time_slot: slot, destination: trip.destination, trip_id: trip.id, image_url: getPlaceImage(name) })
    setSavedNames((s) => new Set([...s, name]))
    flash(`Saved "${name}"`)
  }

  if (loading) return <div className="shell"><Sidebar /><div className="main"><div className="empty"><span className="spinner dark" style={{ margin: '0 auto' }} /></div></div></div>
  if (!trip) return <div className="shell"><Sidebar /><div className="main"><div className="page"><div className="alert alert-error">{error || 'Trip not found'}</div></div></div></div>

  const days = itinerary?.itinerary_days || []

  return (
    <div className="shell">
      <Sidebar />
      <div className="main">
        <TopBar placeholder="Search this itinerary…" />
        <div className="page">
          <button className="btn btn-ghost btn-sm" onClick={() => navigate('/dashboard')} style={{ marginBottom: 14 }}><ArrowLeft size={14} /> Back to dashboard</button>

          <div className="hero-dark" style={{ backgroundImage: `linear-gradient(135deg, rgba(15,23,42,.92), rgba(30,41,59,.75)), url(${getPlaceImage(trip.destination, 1200, 400)})`, backgroundSize: 'cover', backgroundPosition: 'center' }}>
            <div>
              <div className="eyebrow row" style={{ color: '#93c5fd', gap: 6 }}><Sparkles size={12} /> {trip.has_itinerary ? 'Live itinerary' : 'Draft trip'}</div>
              <h1>{trip.destination}</h1>
            </div>
            <div className="row">
              <button className="icon-btn" title="Share" onClick={share} style={{ background: 'rgba(255,255,255,.1)', border: 0, color: '#fff' }}><Share2 size={15} /></button>
              <button className="icon-btn" title="Edit trip" onClick={() => navigate('/create-trip', { state: { prefill: trip } })} style={{ background: 'rgba(255,255,255,.1)', border: 0, color: '#fff' }}><Edit2 size={15} /></button>
              {itinerary && <button className="btn btn-sm" style={{ background: '#fff', color: '#0f172a' }} onClick={download}><Download size={14} /> Export</button>}
            </div>
          </div>

          {error && <div className="alert alert-error" style={{ marginTop: 16 }}>{error}</div>}
          <AnimatePresence>{toast && <motion.div className="alert alert-success" initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} style={{ marginTop: 16 }}><Check size={14} style={{ verticalAlign: -2 }} /> {toast}</motion.div>}</AnimatePresence>

          <div className="trip-layout">
            {/* ---- left column: trip meta ---- */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div className="card card-pad meta-list">
                <div className="meta-item"><Calendar size={16} color="var(--primary)" /><div><small>Duration</small>{formatDate(trip.start_date)} – {formatDate(trip.end_date)}<br /><span className="muted" style={{ fontSize: 12 }}>{trip.duration_days} day{trip.duration_days > 1 ? 's' : ''}</span></div></div>
                <div className="meta-item"><Users size={16} color="var(--primary)" /><div><small>Group size</small>{trip.group_size} traveller{trip.group_size > 1 ? 's' : ''}</div></div>
                <div className="meta-item"><Zap size={16} color="var(--accent)" /><div><small>Style & pace</small><span style={{ textTransform: 'capitalize' }}>{trip.travel_style} · {trip.pace}</span></div></div>
                <div className="meta-item"><Briefcase size={16} color="var(--primary)" /><div><small>Daily budget</small>{formatINR(trip.budget_per_day)} / person</div></div>
              </div>
              <div className="card card-pad">
                <small className="eyebrow">Core interests</small>
                <div className="row wrap" style={{ gap: 6, marginTop: 10 }}>{trip.interests.map((i) => <span key={i} className="chip" style={{ textTransform: 'capitalize' }}>{i}</span>)}</div>
                {trip.dietary_restrictions?.length > 0 && <><div className="divider" /><small className="eyebrow">Dietary</small><div className="row wrap" style={{ gap: 6, marginTop: 10 }}>{trip.dietary_restrictions.map((i) => <span key={i} className="chip">{i}</span>)}</div></>}
              </div>
              {itinerary && (
                <div className="cost-box">
                  <small style={{ opacity: 0.85, fontSize: 10, letterSpacing: '.1em', fontWeight: 700 }}>TOTAL ESTIMATED</small>
                  <b>{formatINR(itinerary.total_estimated_cost)}</b>
                  <small style={{ opacity: 0.85 }}>for the whole group · v{itinerary.version} · {itinerary.ai_provider}</small>
                </div>
              )}
              {itinerary && (
                <div className="card card-pad" style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  <small className="eyebrow">Refine with AI</small>
                  <select className="select" value={regenDay} onChange={(e) => setRegenDay(e.target.value)}>
                    <option value="">Whole itinerary</option>
                    {days.map((d) => <option key={d.day} value={d.day}>Only day {d.day}</option>)}
                  </select>
                  <select className="select" value={vibe} onChange={(e) => setVibe(e.target.value)}>
                    <option value="">Keep current vibe ({trip.travel_style})</option>
                    {VIBES.map((v) => <option key={v} value={v}>Switch vibe → {v}</option>)}
                  </select>
                  <textarea className="textarea" style={{ minHeight: 70 }} placeholder="Feedback, e.g. “more street food, fewer museums”" value={feedback} onChange={(e) => setFeedback(e.target.value)} />
                  <button className="btn btn-soft" disabled={generating} onClick={regenerate} style={{ justifyContent: 'center' }}>{generating ? <Loader size={15} /> : <RefreshCw size={15} />} Regenerate</button>
                </div>
              )}
            </div>

            {/* ---- right column: itinerary ---- */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {!itinerary ? (
                <div className="card empty">
                  <div className="stat-icon" style={{ background: 'var(--primary-soft)', color: 'var(--primary)', margin: '0 auto 14px' }}><Zap size={18} /></div>
                  <h3>Your itinerary awaits.</h3>
                  <p>Our AI engine is ready to draft a personalized minute-by-minute plan for your {trip.destination} adventure.</p>
                  <button className="btn btn-primary" disabled={generating} onClick={generate} style={{ margin: '10px auto 0' }}>
                    {generating ? <><span className="spinner" /> Generating…</> : <><Sparkles size={16} /> Generate Itinerary</>}
                  </button>
                </div>
              ) : (
                <>
                  {itinerary.summary && <div className="card card-pad" style={{ borderLeft: '4px solid var(--primary)' }}><small className="eyebrow">Overview</small><p style={{ margin: '6px 0 0', lineHeight: 1.6, color: '#334155' }}>{itinerary.summary}</p></div>}
                  {generating && <div className="alert alert-info row"><span className="spinner dark" /> Regenerating with AI…</div>}
                  {days.map((d, i) => (
                    <motion.div key={d.day} className="card day-card" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}>
                      <div className="day-head">
                        <div className="row">
                          <div className="day-num">{String(d.day).padStart(2, '0')}</div>
                          <div><small className="muted" style={{ fontSize: 12 }}>{d.date}</small><h3 style={{ fontSize: 18 }}>Day {d.day} Overview{d.title ? ` · ${d.title}` : ''}</h3></div>
                        </div>
                        <div style={{ textAlign: 'right' }}><small className="muted" style={{ fontSize: 10, letterSpacing: '.1em', fontWeight: 700 }}>DAILY CAP</small><div style={{ fontFamily: 'var(--font-display)', fontWeight: 800 }}>{formatINR(d.daily_cost)}</div></div>
                      </div>
                      <div className="grid grid-2">
                        <Slot icon={Sun} color="#f59e0b" title="Morning Exploration" text={d.morning} onSave={() => savePlace(d.morning, 'morning')} saved={savedNames} />
                        <Slot icon={Navigation} color="#2563eb" title="Afternoon Journey" text={d.afternoon} onSave={() => savePlace(d.afternoon, 'afternoon')} saved={savedNames} />
                        <Slot icon={Moon} color="#7c3aed" title="Evening Charm" text={d.evening} onSave={() => savePlace(d.evening, 'evening')} saved={savedNames} />
                        <div className="slot">
                          <div className="slot-title"><Coffee size={14} color="#dc2626" /> Cuisine & Dining</div>
                          {(d.dining || []).map((m, j) => {
                            const label = typeof m === 'string' ? m : `${m.name}${m.description ? ` - ${m.description}` : ''}${m.cost ? `, ${m.cost}` : ''}`
                            const name = typeof m === 'string' ? m : m.name
                            return <p key={j} className="row between" style={{ gap: 8 }}><span>• {label}</span><button className="icon-btn" style={{ width: 26, height: 26, flexShrink: 0 }} title="Save" onClick={() => savePlace(label, 'dining')}><Bookmark size={12} fill={savedNames.has(name) ? 'currentColor' : 'none'} /></button></p>
                          })}
                        </div>
                      </div>
                      <div className="grid grid-2">
                        <div className="slot slot-foot"><div className="slot-title"><Hotel size={14} color="var(--primary)" /> Stay</div><p>{d.stay || '—'}</p></div>
                        <div className="slot slot-foot"><div className="slot-title"><Plane size={14} color="var(--primary)" /> Transit</div><p>{d.transit || '—'}</p></div>
                      </div>
                      {d.notes && <p className="muted" style={{ margin: 0, fontSize: 13 }}><Clock size={12} style={{ verticalAlign: -2 }} /> {d.notes}</p>}
                    </motion.div>
                  ))}
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

const Slot = ({ icon: Icon, color, title, text, onSave, saved }) => {
  const name = (text || '').split(' - ')[0].split(' – ')[0].trim().slice(0, 120)
  return (
    <div className="slot">
      <div className="slot-title row between"><span className="row" style={{ gap: 8 }}><Icon size={14} color={color} /> {title}</span><button className="icon-btn" style={{ width: 26, height: 26 }} title="Save place" onClick={onSave}><Bookmark size={12} fill={saved.has(name) ? 'currentColor' : 'none'} /></button></div>
      <p>{text}</p>
    </div>
  )
}

export default TripView
