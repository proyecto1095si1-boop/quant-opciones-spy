import { Handle, Position } from '@xyflow/react'
import { useState } from 'react'
import { api } from '../api'

export default function ScannerNode() {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [tickers, setTickers] = useState('SPY,QQQ,IWM,DIA,XLF')

  const run = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.scanner(tickers)
      setData(res)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={`node scanner-node ${loading ? 'pulsing' : ''}`}>
      <div className="node-header">
        <span className="node-icon">📡</span>
        <span className="node-title">Scanner</span>
      </div>
      <div className="node-body">
        <label className="scanner-label">
          Tickers
          <input
            value={tickers}
            onChange={(e) => setTickers(e.target.value)}
            disabled={loading}
            placeholder="SPY,QQQ,IWM"
          />
        </label>
        <button className="btn-run" onClick={run} disabled={loading}>
          {loading ? 'Escaneando…' : 'Escanear universo'}
        </button>

        {error && <div className="error-box">{error}</div>}

        {data && (
          <>
            {data.top_short?.length > 0 && (
              <div className="scan-section">
                <span className="label bear">Top BEARISH</span>
                {data.top_short.map((t) => (
                  <div key={t.ticker} className="scan-row">
                    <span className="mono">{t.ticker}</span>
                    <span className="bear">{t.puntos}</span>
                    <span className="muted">${t.precio}</span>
                  </div>
                ))}
              </div>
            )}
            {data.top_long?.length > 0 && (
              <div className="scan-section">
                <span className="label bull">Top BULLISH</span>
                {data.top_long.map((t) => (
                  <div key={t.ticker} className="scan-row">
                    <span className="mono">{t.ticker}</span>
                    <span className="bull">+{t.puntos}</span>
                    <span className="muted">${t.precio}</span>
                  </div>
                ))}
              </div>
            )}
            {!data.top_long?.length && !data.top_short?.length && (
              <div className="node-meta">Sin sesgos fuertes en el universo</div>
            )}
          </>
        )}
      </div>
      <Handle type="source" position={Position.Right} id="out" />
    </div>
  )
}
