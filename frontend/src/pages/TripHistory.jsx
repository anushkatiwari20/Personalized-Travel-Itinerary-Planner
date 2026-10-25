import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import TopBar from '../components/TopBar'
import { historyAPI, errorMessage } from '../services/api'

const LABELS = {
  trip_created: { text: 'Trip created', cls: 'badge-blue' },
  trip_updated: { text: 'Trip updated', cls: 'badge-gray' },
  trip_deleted: { text: 'Trip deleted', cls: 'badge-gray' },
  itinerary_generated: { text: 'Itinerary generated', cls: 'badge-green' },
  itinerary_regenerated: { text: 'Regenerated', cls: 'badge-amber' },
  place_saved: { text: 'Place saved', cls: 'badge-blue' },
  exported: { text: 'Exported', cls: 'badge-gray' },
}

const when = (iso) => {
  const d = new Date(iso)
  return d.toLocaleString('en-IN', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

export const TripHistory = () => {
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')

  useEffect(() => {
    historyAPI.list(100).then(setRows).catch((e) => setError(errorMessage(e))).finally(() => setLoading(false))
  }, [])

  const visible = rows.filter((r) => JSON.stringify(r).toLowerCase().includes(search.toLowerCase()))

  return (
    <>
      <TopBar search={search} onSearch={setSearch} placeholder="Search activity…" />
      <div className="page" style={{ maxWidth: 820 }}>
        <div className="page-head"><div className="eyebrow">Audit log</div><h1>Trip Activity</h1></div>
        {error && <div className="alert alert-error">{error}</div>}
        <div className="card card-pad">
          {loading ? <div className="empty"><span className="spinner dark" style={{ margin: '0 auto' }} /></div> : visible.length === 0 ? (
            <div className="empty"><h3>No activity yet</h3><p>Everything you do — creating, generating, saving — shows up here.</p></div>
          ) : (
            <div className="timeline">
              {visible.map((r) => {
                const l = LABELS[r.action] || { text: r.action, cls: 'badge-gray' }
                const d = r.details || {}
                return (
                  <div key={r.id} className="tl-item">
                    <div className="row" style={{ gap: 8 }}><span className={`badge ${l.cls}`}>{l.text}</span><small className="muted">{when(r.created_at)}</small></div>
                    <b style={{ marginTop: 4 }}>{d.destination || d.name || '—'}</b>
                    <small>
                      {d.day ? `Day ${d.day} · ` : ''}{d.feedback ? `“${d.feedback}” · ` : ''}{d.format ? `${d.format} · ` : ''}
                      {r.trip_id && <Link to={`/trips/${r.trip_id}`} style={{ color: 'var(--primary)', fontWeight: 600 }}>Open trip →</Link>}
                    </small>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </>
  )
}

export default TripHistory
