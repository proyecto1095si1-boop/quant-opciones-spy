const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path, params = {}, options = {}) {
  const url = new URL(`${BASE}${path}`)
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') url.searchParams.set(k, v)
  })
  const res = await fetch(url.toString(), options)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  health: () => request('/health'),
  analisis: (ticker = 'SPY') => request('/analisis', { ticker }),
  senal: (params = {}) => request('/senal', { ticker: 'SPY', ...params }),
  opciones: (params = {}) => request('/opciones', { ticker: 'SPY', ...params }),
  greeks: (params) => request('/greeks', params),

  paperEstado: () => request('/paper/estado'),
  paperPosiciones: () => request('/paper/posiciones'),
  paperHistorial: (limit = 20) => request('/paper/historial', { limit }),
  paperAbrir: (ticker = 'SPY', qty = 1) =>
    request('/paper/abrir', { ticker, qty, usar_senal: true }, { method: 'POST' }),
  paperCerrar: (position_id, premium_salida) =>
    request('/paper/cerrar', { position_id, premium_salida }, { method: 'POST' }),
  paperReset: (cash = 100000) =>
    request('/paper/reset', { cash }, { method: 'POST' }),
}
