import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Plus, MapPin, Calendar, Users, Trash2, Plane, CheckCircle2, Clock } from 'lucide-react'
import TopBar from '../components/TopBar'
import { tripsAPI, errorMessage } from '../services/api'
import { getPlaceImage } from '../utils/placeImages'
import { formatDate, formatINR, getUser } from '../utils/auth'

export const Dashboard = () => {
  const navigate = useNavigate()
  const [trips, setTrips] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const user = getUser()

  const load = async () => {
    try {
      setTrips(await tripsAPI.list())
    } catch (e) {
      setError(errorMessage(e))
    } finally {
      setLoading(false)
    }
  }
  useEffect(() => { load() }, [])

  const remove = async (id) => {
    if (!window.confirm('Delete this trip and its itinerary?')) return
    await tripsAPI.remove(id)
    setTrips((t) => t.filter((x) => x.id !== id))
  }

  const today = new Date().toISOString().slice(0, 10)
  const upcoming = trips.filter((t) => t.start_date >= today).length
  const generated = trips.filter((t) => t.has_itinerary).length
  const visible = trips.filter((t) => t.destination.toLowerCase().includes(search.toLowerCase()))

  return (
    <>
      <TopBar search={search} onSearch={setSearch} />
      <div className="page">
        <div className="page-head row between">
          <div>
            <div className="eyebrow">Welcome back, {user?.name?.split(' ')[0] || 'traveler'}</div>
            <h1>Overview</h1>
          </div>
          <Link to="/create-trip" className="btn btn-primary"><Plus size={16} /> Plan New Trip</Link>
        </div>

        <div className="grid grid-3" style={{ marginBottom: 26 }}>
          <div className="card stat"><div className="stat-icon" style={{ background: 'var(--primary-soft)', color: 'var(--primary)' }}><Plane size={18} /></div><div><b>{trips.length}</b><small>Total trips</small></div></div>
          <div className="card stat"><div className="stat-icon" style={{ background: '#dcfce7', color: '#16a34a' }}><CheckCircle2 size={18} /></div><div><b>{generated}</b><small>Itineraries ready</small></div></div>
          <div className="card stat"><div className="stat-icon" style={{ background: 'var(--accent-soft)', color: '#d97706' }}><Clock size={18} /></div><div><b>{upcoming}</b><small>Upcoming</small></div></div>
        </div>

        <div className="row between" style={{ marginBottom: 14 }}>
          <h3>Your itineraries</h3>
          <small className="muted">{visible.length} trip{visible.length === 1 ? '' : 's'}</small>
        </div>
        {error && <div className="alert alert-error">{error}</div>}
        {loading ? (
          <div className="empty"><span className="spinner dark" style={{ margin: '0 auto' }} /></div>
        ) : visible.length === 0 ? (
          <div className="card empty">
            <h3>No trips yet</h3>
            <p>Create your first AI-generated itinerary in under a minute.</p>
            <Link to="/create-trip" className="btn btn-primary" style={{ marginTop: 10 }}><Plus size={16} /> Plan a trip</Link>
          </div>
        ) : (
          <div className="grid grid-3">
            {visible.map((t, i) => (
              <motion.div key={t.id} className="card trip-card" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}>
                <div className="cover" onClick={() => navigate(`/trips/${t.id}`)} style={{ cursor: 'pointer' }}>
                  <img src={getPlaceImage(t.destination)} alt={t.destination} />
                  <span className={`badge pill ${t.has_itinerary ? 'badge-green' : 'badge-amber'}`}>{t.has_itinerary ? 'Generated' : 'Draft'}</span>
                </div>
                <div className="body">
                  <div className="row between">
                    <h3>{t.destination}</h3>
                    <button className="icon-btn" onClick={() => remove(t.id)} title="Delete"><Trash2 size={14} /></button>
                  </div>
                  <div className="row muted" style={{ fontSize: 13 }}><Calendar size={14} /> {formatDate(t.start_date)} – {formatDate(t.end_date)}</div>
                  <div className="row muted" style={{ fontSize: 13 }}><Users size={14} /> {t.group_size} traveller{t.group_size > 1 ? 's' : ''} · {t.duration_days} day{t.duration_days > 1 ? 's' : ''}</div>
                  <div className="row between" style={{ marginTop: 4 }}>
                    <span className="chip" style={{ textTransform: 'capitalize' }}><MapPin size={12} /> {t.travel_style}</span>
                    <b style={{ color: 'var(--primary)' }}>{formatINR(t.budget_per_day)}<span className="muted" style={{ fontWeight: 400, fontSize: 12 }}>/day</span></b>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </>
  )
}

export default Dashboard
