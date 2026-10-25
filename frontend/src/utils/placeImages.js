/** Deterministic placeholder imagery for places & destinations (no API key needed). */

const slug = (s = '') =>
  String(s)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '') || 'travel'

export const getPlaceImage = (name, w = 640, h = 420) => `https://picsum.photos/seed/${slug(name)}/${w}/${h}`

export const getDestinationImage = (destination) => getPlaceImage(destination, 1200, 500)
