import { Navigate, Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import { isLoggedIn } from '../utils/auth'

/** App shell: sidebar + content area. Redirects to /login if not authenticated. */
export const AppLayout = () => {
  if (!isLoggedIn()) return <Navigate to="/login" replace />
  return (
    <div className="shell">
      <Sidebar />
      <div className="main">
        <Outlet />
      </div>
    </div>
  )
}

export default AppLayout
