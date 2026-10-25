import { Search, Bell } from 'lucide-react'
import { getUser } from '../utils/auth'

export const TopBar = ({ search, onSearch, placeholder = 'Search destinations, experiences...' }) => {
  const user = getUser()
  const initials = (user?.name || 'U')
    .split(' ')
    .map((p) => p[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
  return (
    <header className="topbar">
      <div className="search input-icon">
        <Search size={16} />
        <input className="input" placeholder={placeholder} value={search ?? ''} onChange={(e) => onSearch?.(e.target.value)} />
      </div>
      <div style={{ flex: 1 }} />
      <button className="icon-btn" title="Notifications"><Bell size={16} /></button>
      <div className="row" style={{ gap: 10 }}>
        <div className="avatar">{initials}</div>
        <div style={{ lineHeight: 1.1 }}>
          <div style={{ fontWeight: 600, fontSize: 14 }}>{user?.name || 'Traveler'}</div>
          <small className="muted">{user?.email}</small>
        </div>
      </div>
    </header>
  )
}

export default TopBar
