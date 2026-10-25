export const saveSession = (data) => {
  localStorage.setItem('tp_token', data.access_token)
  localStorage.setItem('tp_user', JSON.stringify({ id: data.user_id, name: data.name, email: data.email }))
}

export const clearSession = () => {
  localStorage.removeItem('tp_token')
  localStorage.removeItem('tp_user')
}

export const getUser = () => {
  try {
    return JSON.parse(localStorage.getItem('tp_user') || 'null')
  } catch {
    return null
  }
}

export const isLoggedIn = () => Boolean(localStorage.getItem('tp_token'))

export const formatINR = (n) => `₹${Number(n || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`

export const formatDate = (d) =>
  d ? new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : ''
