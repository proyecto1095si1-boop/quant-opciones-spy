import { create } from 'zustand'
import { api } from './api'

export const useStore = create((set, get) => ({
  ticker: 'SPY',
  timeframe: '1d',

  loading: false,
  error: null,
  lastRun: null,

  analisis: null,
  senal: null,

  paper: null,
  paperLoading: false,

  setTicker: (ticker) => set({ ticker: ticker.toUpperCase() }),
  setTimeframe: (timeframe) => set({ timeframe }),

  runAnalysis: async () => {
    const { ticker } = get()
    set({ loading: true, error: null })
    try {
      const [analisis, senal] = await Promise.all([
        api.analisis(ticker),
        api.senal({ ticker }),
      ])
      set({
        analisis,
        senal,
        loading: false,
        lastRun: new Date().toISOString(),
      })
    } catch (e) {
      set({ loading: false, error: e.message || 'Error al analizar' })
    }
  },

  refreshPaper: async () => {
    set({ paperLoading: true })
    try {
      const paper = await api.paperEstado()
      set({ paper, paperLoading: false })
    } catch (e) {
      set({ paperLoading: false })
    }
  },

  openPaperFromSignal: async (qty = 1) => {
    const { ticker, refreshPaper } = get()
    set({ paperLoading: true, error: null })
    try {
      const result = await api.paperAbrir(ticker, qty)
      await refreshPaper()
      set({ paperLoading: false })
      return result
    } catch (e) {
      set({ paperLoading: false, error: e.message })
      throw e
    }
  },

  clear: () => set({ analisis: null, senal: null, error: null, lastRun: null }),
}))
