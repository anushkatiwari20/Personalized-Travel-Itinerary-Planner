import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Bookmark, Trash2, Sun, Moon, Navigation, Coffee, MapPin } from 'lucide-react'
import TopBar from '../components/TopBar'
import { savedAPI, errorMessage } from '../services/api'
import { getPlaceImage } from '../utils/placeImages'

const SLOT_ICON = { morning: Sun, afternoon: Navigation, evening: Moon, dining: Coffee }

export const SavedPlaces = () => {
  const [places, setPlaces] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')

  useEffect(() => {
    savedAPI.list().then(setPlaces).catch((e) => setError(errorMessage(e))).finally(() => setLoading(false))
  }, [])

  const remove = async (id) => {
    await savedAPI.remove(id)
    setPlaces((p) => p.filter((x) => x.id !== id))
  }

  const visible = places.filter((p) => `${p.name} ${p.destination || ''}`.toLowerCase().includes(search.toLowerCase()))

  return (
    <>
      <TopBar search={search} onSearch={setSearch} placeholder="Search saved places…" />
      <div className="page">
        <div className="page-head"><div className="eyebrow">Your collection</div><h1>Saved Places</h1></div>
        {error && <div className="alert alert-error">{error}</div>}
        {loading ? <div className="empty"><span className="spinner dark" style={{ margin: '0 auto' }} /></div> : visible.length === 0 ? (
          <div className="card empty">
            <Bookmark size={28} style={{ margin: '0 auto 10px', color: 'var(--primary)' }} />
            <h3>Nothing saved yet</h3>
            <p>Open any itinerary and tap the bookmark icon next to a place to save it here.</p>
            <Link to="/dashboard" className="btn btn-primary" style={{ marginTop: 10 }}>Go to my trips</Link>
          </div>
        ) : (
          <div className="grid grid-3">
            {visible.map((p, i) => {
              const Icon = SLOT_ICON[p.time_slot] || MapPin
              return (
                <motion.div key={p.id} className="card trip-card" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }}>
                  <div className="cover"><img src={p.image_url || getPlaceImage(p.name)} alt={p.name} loading="lazy" />{p.destination && <span className="badge badge-blue pill" style={{ background: '#fff' }}>{p.destination}</span>}</div>
                  <div className="body">
                    <div className="row between"><h3 style={{ fontSize: 16, fontStyle: 'italic' }}>{p.name}</h3><button className="icon-btn" onClick={() => remove(p.id)} title="Remove"><Trash2 size={14} /></button></div>
                    <p className="muted" style={{ margin: 0, fontSize: 13, lineHeight: 1.5, display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>{p.description}</p>
                    <div className="row between" style={{ marginTop: 4 }}>
                      <span className="chip" style={{ textTransform: 'capitalize' }}><Icon size={12} /> {p.time_slot || p.category}</span>
                      {p.trip_id && <Link to={`/trips/${p.trip_id}`} style={{ fontSize: 12, color: 'var(--primary)', fontWeight: 600 }}>View trip →</Link>}
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </div>
        )}
      </div>
    </>
  )
}

export default SavedPlaces
