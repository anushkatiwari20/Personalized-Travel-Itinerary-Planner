import axios from 'axios'

const BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api').replace(/\/$/, '')

export const api = axios.create({ baseURL: BASE_URL, timeout: 180000 })

// Attach JWT on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('tp_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Auto-logout on 401
api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401 && !err.config?.url?.includes('/auth/')) {
      localStorage.removeItem('tp_token')
      localStorage.removeItem('tp_user')
      if (!window.location.pathname.startsWith('/login')) window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const errorMessage = (err, fallback = 'Something went wrong') => {
  const d = err?.response?.data?.detail
  if (Array.isArray(d)) return d.map((x) => x.msg).join(', ')
  return d || err?.message || fallback
}

// ---------- Auth ----------
export const authAPI = {
  register: (data) => api.post('/auth/register', data).then((r) => r.data),
  login: (data) => api.post('/auth/login', data).then((r) => r.data),
  me: () => api.get('/auth/me').then((r) => r.data),
}

// ---------- Trips & itineraries ----------
export const tripsAPI = {
  create: (data) => api.post('/trips', data).then((r) => r.data),
  list: () => api.get('/trips').then((r) => r.data),
  get: (id) => api.get(`/trips/${id}`).then((r) => r.data),
  update: (id, data) => api.patch(`/trips/${id}`, data).then((r) => r.data),
  remove: (id) => api.delete(`/trips/${id}`).then((r) => r.data),
  generate: (id) => api.post(`/trips/${id}/generate`).then((r) => r.data),
  regenerate: (id, data = {}) => api.post(`/trips/${id}/regenerate`, data).then((r) => r.data),
  itinerary: (id) => api.get(`/trips/${id}/itinerary`).then((r) => r.data),
  exportMarkdown: (id) => api.get(`/trips/${id}/export`, { responseType: 'text' }).then((r) => r.data),
}

// ---------- Explore ----------
export const exploreAPI = {
  vibes: () => api.get('/explore/vibes').then((r) => r.data),
  destinations: (params) => api.get('/explore/destinations', { params }).then((r) => r.data),
  destination: (slug) => api.get(`/explore/destinations/${slug}`).then((r) => r.data),
}

// ---------- Saved places ----------
export const savedAPI = {
  list: () => api.get('/saved-places').then((r) => r.data),
  add: (data) => api.post('/saved-places', data).then((r) => r.data),
  remove: (id) => api.delete(`/saved-places/${id}`).then((r) => r.data),
}

// ---------- Preferences & history ----------
export const prefsAPI = {
  get: () => api.get('/preferences').then((r) => r.data),
  set: (data) => api.put('/preferences', data).then((r) => r.data),
}

export const historyAPI = {
  list: (limit = 50) => api.get('/history', { params: { limit } }).then((r) => r.data),
}
