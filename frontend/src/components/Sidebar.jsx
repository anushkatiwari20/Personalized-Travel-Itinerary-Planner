import { NavLink, useNavigate } from 'react-router-dom'
import { LayoutDashboard, PlusCircle, Compass, Bookmark, History, LogOut, Plane, Sparkles } from 'lucide-react'
import { clearSession } from '../utils/auth'

const links = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/create-trip', label: 'Plan New Trip', icon: PlusCircle },
  { to: '/explore', label: 'Explore', icon: Compass },
  { to: '/saved', label: 'Saved Places', icon: Bookmark },
  { to: '/history', label: 'Trip History', icon: History },
]

export const Sidebar = () => {
  const navigate = useNavigate()
  const logout = () => {
    clearSession()
    navigate('/login')
  }
  return (
    <aside className="sidebar">
      <NavLink to="/dashboard" className="brand">
        <div className="brand-mark"><Plane size={16} /></div>
        Travel<span>Planner</span>
      </NavLink>
      {links.map(({ to, label, icon: Icon }) => (
        <NavLink key={to} to={to} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <Icon size={18} /> {label}
        </NavLink>
      ))}
      <div className="sidebar-foot">
        <div className="upgrade-card">
          <div className="row" style={{ gap: 6, marginBottom: 6, opacity: 0.85, fontSize: 11, letterSpacing: '.1em' }}>
            <Sparkles size={12} /> PREMIUM TRAVEL
          </div>
          <b>Get unlimited AI planning</b>
          and offline maps.
          <br />
          <button className="btn btn-sm" style={{ background: '#fff', color: '#1d4ed8', marginTop: 10 }}>Upgrade Now</button>
        </div>
        <button className="nav-link" onClick={logout} style={{ background: 'none', border: 0, width: '100%' }}>
          <LogOut size={18} /> Sign out
        </button>
      </div>
    </aside>
  )
}

export default Sidebar
