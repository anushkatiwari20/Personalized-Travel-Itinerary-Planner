import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from './components/Layout'
import Landing from './pages/Landing'
import { Login, Register } from './pages/Auth'
import Dashboard from './pages/Dashboard'
import CreateTrip from './pages/CreateTrip'
import TripView from './pages/TripView'
import Explore from './pages/Explore'
import SavedPlaces from './pages/SavedPlaces'
import TripHistory from './pages/TripHistory'
import { isLoggedIn } from './utils/auth'

const Protected = ({ children }) => (isLoggedIn() ? children : <Navigate to="/login" replace />)

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/create-trip" element={<CreateTrip />} />
          <Route path="/explore" element={<Explore />} />
          <Route path="/saved" element={<SavedPlaces />} />
          <Route path="/history" element={<TripHistory />} />
        </Route>
        {/* TripView renders its own shell (sidebar + topbar) */}
        <Route path="/trips/:tripId" element={<Protected><TripView /></Protected>} />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
