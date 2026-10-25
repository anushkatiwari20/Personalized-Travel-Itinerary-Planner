import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Compass, Flame, Star, X, Sparkles, Clock, Wallet, MapPin, Waves, Mountain, Building2, Landmark, UtensilsCrossed, Music, Tent, Palmtree } from 'lucide-react'
import TopBar from '../components/TopBar'
import { exploreAPI, errorMessage } from '../services/api'
import { formatINR } from '../utils/auth'

const VIBE_ICONS = { all: Compass, beach: Waves, mountain: Mountain, city: Building2, cultural: Landmark, food: UtensilsCrossed, nightlife: Music, adventure: Tent, relaxed: Palmtree }

export const Explore = () => {
  const navigate = useNavigate()
  const [vibes, setVibes] = useState(['all'])
  const [vibe, setVibe] = useState('all')
  const [search, setSearch] = useState('')
  const [items, setItems] = useState([])
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => { exploreAPI.vibes().then(setVibes).catch(() => {}) }, [])
  useEffect(() => {
    setLoading(true)
    exploreAPI.destinations({ vibe, q: search || undefined }).then(setItems).catch((e) => setError(errorMessage(e))).finally(() => setLoading(false))
  }, [vibe, search])

  const startPlanning = (d) => {
    navigate('/create-trip', { state: { prefill: { destination: `${d.name}, ${d.country}`, budget_per_day: d.avg_budget_per_day, travel_style: d.vibes.includes('adventure') ? 'adventure' : d.vibes.includes('relaxed') ? 'relaxed' : 'cultural' } } })
  }

  return (
    <>
      <TopBar search={search} onSearch={setSearch} placeholder="Search destinations…" />
      <div className="page">
        <div className="page-head"><div className="eyebrow">Discover</div><h1>Explore destinations</h1></div>

        <div className="card card-pad" style={{ marginBottom: 22 }}>
          <div className="row" style={{ marginBottom: 12 }}><Compass size={16} color="var(--primary)" /><b>Popular Vibe</b></div>
          <div className="row wrap" style={{ gap: 8 }}>
            {vibes.map((v) => { const Icon = VIBE_ICONS[v] || Compass; return <button key={v} className={`chip chip-btn ${vibe === v ? 'active' : ''}`} onClick={() => setVibe(v)} style={{ textTransform: 'capitalize', padding: '9px 16px' }}><Icon size={13} /> {v}</button> })}
          </div>
        </div>

        <div className="row between" style={{ marginBottom: 14 }}>
          <div className="row"><Flame size={16} color="#f97316" /><b>Trending Now</b><small className="muted" style={{ textTransform: 'capitalize' }}>· {vibe === 'all' ? 'everywhere' : vibe}</small></div>
          <small className="muted">{items.length} destinations</small>
        </div>
        {error && <div className="alert alert-error">{error}</div>}
        {loading ? <div className="empty"><span className="spinner dark" style={{ margin: '0 auto' }} /></div> : (
          <div className="grid grid-4">
            {items.map((d, i) => (
              <motion.div key={d.slug} className="card dest-card" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }} onClick={() => setSelected(d)}>
                <div className="cover"><img src={d.image_url} alt={d.name} loading="lazy" /><span className="badge badge-blue pill" style={{ background: '#fff' }}>{d.vibes[0]}</span></div>
                <div style={{ padding: 14 }}>
                  <div className="row between"><b style={{ fontFamily: 'var(--font-display)', fontStyle: 'italic' }}>{d.name}, {d.country}</b><span className="row" style={{ gap: 3, fontSize: 12, color: '#f59e0b', fontWeight: 700 }}><Star size={12} fill="#f59e0b" /> {d.rating}</span></div>
                  <div className="row between muted" style={{ fontSize: 12, marginTop: 8 }}><span>{(d.reviews / 1000).toFixed(0)}k reviews</span><b style={{ color: 'var(--ink)' }}>{'₹'.repeat(d.budget_level)}</b></div>
                </div>
              </motion.div>
            ))}
            {items.length === 0 && <div className="empty" style={{ gridColumn: '1/-1' }}><h3>No matches</h3><p>Try another vibe or search term.</p></div>}
          </div>
        )}
      </div>

      <AnimatePresence>
        {selected && (
          <motion.div className="modal-bg" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setSelected(null)}>
            <motion.div className="modal" initial={{ scale: 0.95, y: 20 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.95, y: 20 }} onClick={(e) => e.stopPropagation()} style={{ position: 'relative' }}>
              <div style={{ position: 'relative' }}>
                <img src={selected.image_url} alt={selected.name} />
                <div style={{ position: 'absolute', left: 22, bottom: 22, color: '#fff', textShadow: '0 2px 12px rgba(0,0,0,.6)' }}>
                  <span className="badge badge-blue" style={{ marginBottom: 8 }}><Flame size={11} /> Popular right now</span>
                  <h2 style={{ fontSize: 34, fontStyle: 'italic' }}>{selected.name}, {selected.country}</h2>
                  <div className="row" style={{ gap: 4, fontSize: 13 }}><Star size={13} fill="#f59e0b" color="#f59e0b" /> {selected.rating} ({(selected.reviews / 1000).toFixed(0)}k reviews)</div>
                </div>
              </div>
              <div className="modal-body">
                <button className="icon-btn modal-close" onClick={() => setSelected(null)}><X size={16} /></button>
                <div><div className="slot-title" style={{ color: 'var(--primary)' }}><MapPin size={13} /> Overview</div><p style={{ color: '#334155', lineHeight: 1.6, margin: '8px 0 0' }}>{selected.overview}</p></div>
                <div className="grid grid-2">
                  <div><div className="slot-title" style={{ color: 'var(--primary)' }}><Clock size={13} /> Best time</div><p style={{ margin: '6px 0 0' }}>{selected.best_time}</p></div>
                  <div><div className="slot-title" style={{ color: 'var(--primary)' }}><Wallet size={13} /> Avg budget</div><p style={{ margin: '6px 0 0' }}>{formatINR(selected.avg_budget_per_day)} / day</p></div>
                </div>
                <div><div className="slot-title" style={{ color: 'var(--primary)' }}><Sparkles size={13} /> Destination highlights</div><div className="row wrap" style={{ gap: 6, marginTop: 8 }}>{selected.highlights.map((h) => <span key={h} className="chip"># {h}</span>)}</div></div>
                <button className="btn btn-primary btn-lg" style={{ justifyContent: 'center', marginTop: 'auto' }} onClick={() => startPlanning(selected)}><Sparkles size={16} /> Start Planning This Trip</button>
                <small className="muted" style={{ textAlign: 'center', letterSpacing: '.08em', fontSize: 10, textTransform: 'uppercase' }}>Customize dates, budget, and travel style</small>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}

export default Explore
