import { Handle, Position } from '@xyflow/react'
import { useStore } from '../store'

const BIAS_COLOR = {
  BULLISH: 'var(--bull)',
  BEARISH: 'var(--bear)',
  NEUTRAL: 'var(--neutral)',
}

export default function QuantEngineNode() {
  const { loading, error, analisis, senal, runAnalysis, lastRun } = useStore()

  const bias = senal?.bias || analisis?.sesgo?.bias
  const razones = analisis?.sesgo?.razones || []
  const patrones = analisis?.patrones || []
  const precio = analisis?.sesgo?.precio
  const sma20 = analisis?.sesgo?.sma20
  const sma50 = analisis?.sesgo?.sma50

  return (
    <div className={`node quant-node ${loading ? 'pulsing' : ''}`}>
      <Handle type="target" position={Position.Left} id="in" />
      <div className="node-header">
        <span className="node-icon">🧠</span>
        <span className="node-title">Quant Engine</span>
      </div>
      <div className="node-body">
        <button
          className="btn-run"
          onClick={runAnalysis}
          disabled={loading}
        >
          {loading ? 'Analizando…' : 'Ejecutar análisis'}
        </button>

        {error && <div className="error-box">{error}</div>}

        {bias && (
          <div className="bias-badge" style={{ borderColor: BIAS_COLOR[bias] }}>
            <span className="bias-label" style={{ color: BIAS_COLOR[bias] }}>
              {bias}
            </span>
            {precio && (
              <span className="bias-price">${precio.toFixed(2)}</span>
            )}
          </div>
        )}

        {(sma20 || sma50) && (
          <div className="sma-row">
            {sma20 != null && <span>SMA20 {sma20}</span>}
            {sma50 != null && <span>SMA50 {sma50}</span>}
          </div>
        )}

        {razones.length > 0 && (
          <ul className="razones">
            {razones.slice(0, 3).map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        )}

        {patrones.length > 0 && (
          <div className="patrones">
            {patrones.map((p, i) => (
              <span key={i} className={`patron-tag ${p.direccion}`}>
                {p.descripcion}
              </span>
            ))}
          </div>
        )}

        {lastRun && (
          <div className="node-meta">
            {new Date(lastRun).toLocaleTimeString()}
          </div>
        )}
      </div>
      <Handle type="source" position={Position.Right} id="out" />
    </div>
  )
}
